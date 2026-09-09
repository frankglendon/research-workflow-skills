"""CLI handoff between installed MCP tools and local retrieval storage."""
import json
from pathlib import Path
from . import retrieval
from .contracts import GateError

COMMANDS = {'retrieval-init', 'retrieval-add', 'retrieval-next', 'retrieval-record', 'retrieval-fail',
            'retrieval-status', 'retrieval-manifest', 'retrieval-local', 'retrieval-ledger'}


def register(commands):
    fields = {'retrieval-init': ['plan'], 'retrieval-add': ['job'], 'retrieval-record': ['request-id', 'response'],
              'retrieval-fail': ['request-id', 'code'], 'retrieval-local': ['query'], 'retrieval-ledger': ['output']}
    for name in sorted(COMMANDS):
        parser = commands.add_parser(name)
        parser.add_argument('--workspace', required=True)
        for field in fields.get(name, []):
            parser.add_argument('--' + field, required=True)
        if name == 'retrieval-local':
            parser.add_argument('--top-k', type=int, default=5)


def _read(path):
    source = Path(path)
    if source.stat().st_size > 10_000_000:
        raise GateError('Retrieval JSON exceeds the import limit')
    return json.loads(source.read_text(encoding='utf-8'))


def dispatch(args):
    name, workspace = args.command, args.workspace
    if name == 'retrieval-init':
        return retrieval.initialize(workspace, _read(args.plan))
    if name == 'retrieval-add':
        return retrieval.add(workspace, _read(args.job))
    if name == 'retrieval-next':
        return {'request': retrieval.next_request(workspace)}
    if name == 'retrieval-record':
        return retrieval.record(workspace, args.request_id, _read(args.response))
    if name == 'retrieval-fail':
        return retrieval.fail(workspace, args.request_id, args.code)
    if name == 'retrieval-status':
        return retrieval.status(workspace)
    if name == 'retrieval-manifest':
        return retrieval.manifest(workspace)
    if name == 'retrieval-local':
        return {'candidates': retrieval.search_local(workspace, args.query, args.top_k)}
    if name == 'retrieval-ledger':
        result = retrieval.ledger(workspace)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
        return {'ledger_file': str(output), 'documents': len(result['documents']), 'status': result['status']}
    raise GateError('Unknown retrieval command')
