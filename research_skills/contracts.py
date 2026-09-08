"""Deterministic contracts shared by host-driven research workflows."""
import hashlib
import json
import re
from urllib.parse import urlparse


class GateError(ValueError):
    pass


def fingerprint(value):
    raw = value if isinstance(value, bytes) else json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def review_rows(expected, reviews):
    ids = [r.get("row") for r in reviews]
    if any(type(n) is not int for n in ids) or len(ids) != len(set(ids)):
        raise GateError("Review rows must be unique integers")
    if set(ids) != set(expected):
        raise GateError("Mandatory row review coverage is incomplete")
    if any(r.get("verdict") not in {"clean", "issue", "uncertain"} for r in reviews):
        raise GateError("Unknown review verdict")
    return reviews


def validate_evidence(ledger):
    docs = ledger.get("documents", [])
    claims = ledger.get("claims", [])
    by_id = {d.get("id"): d for d in docs}
    if not docs or not claims or len(by_id) != len(docs) or None in by_id:
        raise GateError("Evidence documents and claims require unique IDs")
    if len({c.get("id") for c in claims}) != len(claims):
        raise GateError("Duplicate claim IDs")
    for doc in docs:
        parsed = urlparse(doc.get("url", ""))
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise GateError("Evidence URL must be HTTP(S)")
        if not doc.get("text") or doc.get("sha256") != fingerprint(doc["text"].encode()):
            raise GateError("Source document hash is missing or inconsistent")
    for claim in claims:
        if not claim.get("id") or not claim.get("statement"):
            raise GateError("Claim ID and statement are required")
        if claim.get("status") != "supported" or not claim.get("evidence"):
            raise GateError("Unresolved claims cannot enter final delivery")
        quotes = []
        for ev in claim["evidence"]:
            doc = by_id.get(ev.get("document_id"))
            quote = ev.get("quote", "")
            if doc is None or not quote or quote not in doc["text"]:
                raise GateError("Citation quote does not occur in source text")
            quotes.append(quote)
        if claim.get("evidence_sha256") != fingerprint(claim["evidence"]):
            raise GateError("Semantic review must bind the current evidence")
        if claim.get("reviewed_statement_sha256") != fingerprint(claim["statement"].encode()):
            raise GateError("Semantic review must bind the current statement")
        numbers = lambda s: set(re.findall(r"\d+(?:[.,]\d+)*(?:%|％)?", s))
        if not numbers(claim["statement"]).issubset(numbers(" ".join(quotes))):
            raise GateError("Claim contains a number absent from quoted evidence")
        if not claim.get("scope") or claim.get("semantic_reviewed") is not True:
            raise GateError("Claim requires explicit scope and semantic review")
    return {"documents": len(docs), "claims": len(claims)}
