"""Host-driven MCP retrieval journal and lexical evidence candidate retrieval.

The host calls its installed MCP tools. This module never starts a server,
stores API credentials, performs network calls, or approves source meaning.
"""
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import sqlite3
import time
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import uuid

from .contracts import GateError, fingerprint


def canonical_url(value):
    if not isinstance(value, str) or len(value) > 8192:
        raise GateError('Source URL must be a bounded HTTP(S) URL')
    parsed = urlsplit(value)
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password:
        raise GateError('Source URL must be HTTP(S) without embedded credentials')
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    if any(k.lower() in {'api_key', 'apikey', 'token', 'access_token', 'signature'} for k, _ in pairs):
        raise GateError('Credential-bearing URLs cannot enter the retrieval journal')
    pairs = [(k, v) for k, v in pairs if not k.lower().startswith('utm_') and k.lower() not in {'fbclid', 'gclid'}]
    host = parsed.netloc.lower()
    if (parsed.scheme == 'https' and parsed.port == 443) or (parsed.scheme == 'http' and parsed.port == 80):
        host = host.rsplit(':', 1)[0]
    return urlunsplit((parsed.scheme, host, parsed.path or '/', urlencode(sorted(pairs)), ''))


def _text(value, label, limit=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise GateError(f'{label} must be nonempty bounded text')
    return value.strip()


def _integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise GateError('Retrieval budget or limit is outside the supported range')
    return value


def _job(raw, max_results):
    if not isinstance(raw, dict) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', str(raw.get('id', ''))):
        raise GateError('Retrieval job requires a short stable ID')
    kind = raw.get('kind', 'search')
    provider = raw.get('provider', 'tavily')
    if kind not in {'search', 'extract'} or provider not in {'tavily', 'firecrawl'}:
        raise GateError('Unsupported retrieval operation or provider')
    if kind == 'search' and provider != 'tavily':
        raise GateError('Search uses Tavily; Firecrawl is an explicit page extraction option')
    if kind == 'search':
        query = _text(raw.get('query'), 'Query')
        args = {'query': query, 'max_results': max_results, 'search_depth': 'basic', 'include_raw_content': False}
        for key in ('include_domains', 'exclude_domains'):
            if key in raw:
                domains = raw[key]
                if not isinstance(domains, list) or len(domains) > 20 or any(not isinstance(d, str) or not re.fullmatch(r'[A-Za-z0-9.-]+', d) for d in domains):
                    raise GateError('Domain filters must be a bounded list of hostnames')
                args[key] = sorted(set(d.lower() for d in domains))
        for key in ('start_date', 'end_date'):
            if key in raw:
                try:
                    datetime.strptime(raw[key], '%Y-%m-%d')
                except (TypeError, ValueError):
                    raise GateError('Date filters must be valid YYYY-MM-DD dates') from None
                args[key] = raw[key]
        if args.get('start_date', '') > args.get('end_date', '9999-12-31'):
            raise GateError('Start date must precede end date')
        tool = 'tavily_search'
        identity = {**args, 'query': ' '.join(query.casefold().split())}
    else:
        url = canonical_url(raw.get('url'))
        args = {'urls': [url], 'extract_depth': 'basic', 'format': 'markdown'} if provider == 'tavily' else {
            'url': url, 'formats': ['markdown'], 'onlyMainContent': True}
        tool = 'tavily_extract' if provider == 'tavily' else 'firecrawl_scrape'
        identity = args
    return {'id': raw['id'], 'kind': kind, 'provider': provider, 'tool': tool, 'arguments': args,
            'gap': _text(raw.get('gap'), 'Evidence gap'), 'identity': fingerprint([provider, kind, identity]),
            'state': 'pending', 'attempts': 0, 'available_at': 0, 'request_id': None}


def _path(workspace, create=False):
    folder = Path(workspace).resolve() / '.retrieval'
    if folder.is_symlink() or (folder / 'state.sqlite3').is_symlink():
        raise GateError('Retrieval storage cannot be a symlink')
    if create:
        folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'state.sqlite3'
    if not create and not path.is_file():
        raise GateError('Initialize this retrieval workspace first')
    return path


@contextmanager
def _state(workspace):
    connection = sqlite3.connect(_path(workspace), timeout=5)
    try:
        connection.execute('BEGIN IMMEDIATE')
        row = connection.execute('SELECT payload FROM journal WHERE id=1').fetchone()
        if row is None:
            raise GateError('Retrieval journal is not initialized')
        state = json.loads(row[0])
        yield state
        connection.execute('UPDATE journal SET payload=? WHERE id=1', (json.dumps(state, ensure_ascii=False),))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize(workspace, plan):
    if plan.get('schema_version') != 1 or not isinstance(plan.get('jobs'), list) or not plan['jobs']:
        raise GateError('Plan requires schema_version=1 and initial jobs')
    state = {'schema_version': 1, 'session_id': uuid.uuid4().hex, 'jobs': [], 'documents': {},
             'max_calls': _integer(plan.get('max_calls', 24), 1, 100),
             'max_attempts': _integer(plan.get('max_attempts', 4), 1, 4),
             'max_results': _integer(plan.get('max_results', 5), 1, 10)}
    for raw in plan['jobs']:
        _add(state, raw)
    connection = sqlite3.connect(_path(workspace, create=True), timeout=5)
    try:
        connection.execute('BEGIN IMMEDIATE')
        connection.execute('CREATE TABLE IF NOT EXISTS journal (id INTEGER PRIMARY KEY, payload TEXT NOT NULL)')
        if connection.execute('SELECT id FROM journal').fetchone():
            raise GateError('Retrieval workspace already initialized')
        connection.execute('INSERT INTO journal VALUES (1, ?)', (json.dumps(state, ensure_ascii=False),))
        connection.commit()
    finally:
        connection.close()
    return manifest(workspace)


def _add(state, raw):
    candidate = _job(raw, state['max_results'])
    existing = next((j for j in state['jobs'] if j['identity'] == candidate['identity']), None)
    if existing is not None:
        gaps = existing.setdefault('related_gaps', [])
        if candidate['gap'] != existing['gap'] and candidate['gap'] not in gaps:
            gaps.append(candidate['gap'])
        return
    if len(state['jobs']) >= 100 or any(j['id'] == candidate['id'] for j in state['jobs']):
        raise GateError('Duplicate job ID or too many retrieval jobs')
    state['jobs'].append(candidate)


def add(workspace, raw):
    with _state(workspace) as state:
        _add(state, raw)
    return manifest(workspace)


def next_request(workspace):
    with _state(workspace) as state:
        if any(j['state'] == 'inflight' for j in state['jobs']):
            raise GateError('Record or explicitly fail the outstanding request before another call')
        pending = [j for j in state['jobs'] if j['state'] in {'pending', 'retry'}]
        if not pending:
            return None
        if sum(j['attempts'] for j in state['jobs']) >= state['max_calls']:
            raise GateError('Retrieval call budget exhausted; report the remaining gaps')
        job = pending[0]
        if job['available_at'] > time.time():
            raise GateError('Rate-limit backoff is still active; do not issue another request')
        job.update(state='inflight', request_id=uuid.uuid4().hex, attempts=job['attempts'] + 1)
        return {'request_id': job['request_id'], 'job_id': job['id'], 'provider': job['provider'],
                'tool': job['tool'], 'arguments': job['arguments']}


def _inflight(state, request_id):
    job = next((j for j in state['jobs'] if j['request_id'] == request_id and j['state'] == 'inflight'), None)
    if job is None:
        raise GateError('Request is stale, already recorded, or belongs to another workspace')
    return job


def fail(workspace, request_id, code):
    if code not in {'429', 'timeout', 'unavailable', 'interrupted', 'invalid_payload', 'extraction_failed', '401', '403', '404'}:
        raise GateError('Use a supported error category, never raw provider errors or credentials')
    with _state(workspace) as state:
        job = _inflight(state, request_id)
        retry = code in {'429', 'timeout', 'unavailable', 'interrupted'} and job['attempts'] < state['max_attempts']
        job.update(state='retry' if retry else 'failed', error_category=code,
                   available_at=time.time() + 2 ** (job['attempts'] - 1) if retry else 0)
    return manifest(workspace)


def _payload(response):
    if not isinstance(response, dict) or response.get('isError') is True or response.get('success') is False:
        raise GateError('MCP returned an error; record a categorized failure')
    if isinstance(response.get('structuredContent'), dict):
        return _payload(response['structuredContent'])
    if isinstance(response.get('content'), list):
        texts = [item.get('text', '') for item in response['content'] if isinstance(item, dict) and item.get('type') == 'text']
        if len(texts) != 1:
            raise GateError('Expected a single JSON text block or structured MCP result')
        try:
            return _payload(json.loads(texts[0]))
        except (ValueError, TypeError):
            raise GateError('MCP response is not supported structured JSON') from None
    return response


def _documents(job, response):
    body = _payload(response)
    if job['provider'] == 'tavily':
        rows = body.get('results')
        if not isinstance(rows, list) or len(rows) > 100:
            raise GateError('Tavily response requires a bounded results list')
        if body.get('failed_results'):
            raise GateError('Extraction reported failed URLs; record a failure or review partial results')
    else:
        data = body.get('data', body)
        if not isinstance(data, dict) or not isinstance(data.get('markdown'), str):
            raise GateError('Firecrawl response requires page markdown, not agent synthesis or structured extraction')
        metadata = data.get('metadata') or {}
        if not isinstance(metadata, dict):
            raise GateError('Firecrawl page metadata must be an object')
        rows = [{'url': metadata.get('sourceURL') or metadata.get('source_url') or metadata.get('url') or job['arguments']['url'],
                 'title': metadata.get('title', ''), 'raw_content': data['markdown']}]
    docs = []
    expected = job['arguments'].get('url') or job['arguments'].get('urls', [None])[0]
    for row in rows:
        if not isinstance(row, dict):
            raise GateError('Search and extract results must be objects')
        url = canonical_url(row.get('url'))
        if expected and url != expected:
            raise GateError('Extracted URL does not match this request; review redirects or response binding')
        kind = 'search_snippet' if job['kind'] == 'search' else 'extracted_page'
        text = row.get('content', '') if kind == 'search_snippet' else row.get('raw_content', '')
        if not isinstance(text, str) or len(text) > 1_000_000:
            raise GateError('Source text is missing, invalid or too large; do not silently truncate it')
        if not text.strip():
            continue
        title = row.get('title') or url
        if not isinstance(title, str) or len(title) > 5000:
            raise GateError('Source title is invalid')
        sha = fingerprint(text.encode('utf-8'))
        docs.append({'id': 'd_' + fingerprint([url, sha, kind])[:24], 'url': url, 'title': title,
                     'text': text, 'sha256': sha, 'source_kind': kind, 'trust': 'untrusted_source_text',
                     'retrieved_at': datetime.now(timezone.utc).isoformat(),
                     'provenance': [{'job_id': job['id'], 'provider': job['provider']}],
                     'semantic_reviewed': False})
    return docs


def record(workspace, request_id, response):
    with _state(workspace) as state:
        job = _inflight(state, request_id)
        docs = _documents(job, response)
        if sum(len(d['text']) for d in state['documents'].values()) + sum(len(d['text']) for d in docs) > 20_000_000:
            raise GateError('Workspace text budget exceeded; narrow the selected pages')
        for doc in docs:
            old = state['documents'].get(doc['id'])
            if old is not None:
                old['provenance'].extend(p for p in doc['provenance'] if p not in old['provenance'])
            else:
                state['documents'][doc['id']] = doc
        job.update(state='done' if docs else 'empty', document_ids=[d['id'] for d in docs])
    return manifest(workspace)


def status(workspace):
    with _state(workspace) as state:
        return {'jobs': state['jobs'], 'max_calls': state['max_calls'], 'max_attempts': state['max_attempts']}


def manifest(workspace):
    with _state(workspace) as state:
        jobs = state['jobs']
        docs = list(state['documents'].values())
        counts = Counter(j['state'] for j in jobs)
        return {'schema_version': 1, 'jobs': len(jobs), 'issued_calls': sum(j['attempts'] for j in jobs),
                'max_calls': state['max_calls'], 'done_jobs': counts['done'], 'empty_jobs': counts['empty'],
                'failed_jobs': counts['failed'], 'inflight_jobs': counts['inflight'],
                'pending_jobs': counts['pending'] + counts['retry'],
                'source_pages': sum(d['source_kind'] == 'extracted_page' for d in docs),
                'search_snippets': sum(d['source_kind'] == 'search_snippet' for d in docs),
                'unique_urls': len({d['url'] for d in docs}),
                'research_verified': False, 'model_calls_by_module': 0}


def ledger(workspace):
    with _state(workspace) as state:
        docs = [d for d in state['documents'].values() if d['source_kind'] == 'extracted_page']
        if any(fingerprint(d['text'].encode('utf-8')) != d['sha256'] for d in docs):
            raise GateError('Stored source content hash changed')
        return {'documents': docs, 'claims': [], 'status': 'unreviewed_candidates'}


def _tokens(text):
    words = re.findall(r'[a-z0-9]+|[\u3400-\u9fff]+', text.casefold())
    result = []
    for word in words:
        if re.fullmatch(r'[\u3400-\u9fff]+', word):
            result.extend(word[i:i + 2] for i in range(max(1, len(word) - 1)))
        else:
            result.append(word)
    return result


def search_local(workspace, query, top_k=5):
    query = _text(query, 'Local query')
    _integer(top_k, 1, 20)
    chunks = []
    for doc in ledger(workspace)['documents']:
        for start in range(0, len(doc['text']), 1050):
            end = min(start + 1200, len(doc['text']))
            quote = doc['text'][start:end]
            chunks.append({'document_id': doc['id'], 'url': doc['url'], 'source_sha256': doc['sha256'],
                           'start': start, 'end': end, 'quote': quote, 'semantic_reviewed': False,
                           '_terms': Counter(_tokens(quote))})
    if not chunks:
        return []
    terms = set(_tokens(query))
    avg = sum(sum(c['_terms'].values()) for c in chunks) / len(chunks) or 1
    df = {t: sum(t in c['_terms'] for c in chunks) for t in terms}
    ranked = []
    for chunk in chunks:
        frequencies = chunk.pop('_terms')
        length = sum(frequencies.values())
        score = 0.0
        for term in terms:
            tf = frequencies[term]
            idf = math.log(1 + (len(chunks) - df[term] + 0.5) / (df[term] + 0.5))
            score += idf * tf * 2.2 / (tf + 1.2 * (0.25 + 0.75 * length / avg))
        if score > 0:
            ranked.append({**chunk, 'score': round(score, 8), 'ranking': 'lexical_bm25'})
    return sorted(ranked, key=lambda c: (-c['score'], c['document_id'], c['start']))[:top_k]
