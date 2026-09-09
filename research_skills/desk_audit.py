"""Structural desk-research diagnostics, never a semantic quality certificate."""
import json
from collections import Counter
from pathlib import Path

ANALYSIS_ROLES = {"analysis", "competitor", "country", "opportunity"}
OTHER_ROLES = {"cover", "setup", "summary", "methods", "future_research", "sources"}


def audit(study):
    questions, pages, answers = (study.get(k, []) for k in ("questions", "pages", "answers"))
    findings = []

    def issue(code, item, reason):
        findings.append({"code": code, "item": item, "reason": reason})

    def index(rows, kind):
        result = {}
        for row in rows:
            key = row.get("id")
            if not isinstance(key, str) or not key.strip() or key in result:
                issue("invalid_id", kind, "Missing or duplicate ID")
            else:
                result[key] = row
        return result

    qi, pi, ai = index(questions, "questions"), index(pages, "pages"), index(answers, "answers")
    if not qi:
        issue("no_questions", "study", "No business questions defined")
    claims = set(study.get("claim_ids", []))
    roles = Counter()
    repeated = {}
    for key, p in pi.items():
        role = p.get("role")
        roles[role or "missing"] += 1
        if role not in ANALYSIS_ROLES | OTHER_ROLES:
            issue("invalid_role", key, "Page role is missing or unknown")
        for q in p.get("question_ids", []):
            if q not in qi:
                issue("unknown_question", key, q)
        for c in p.get("claim_ids", []):
            if c not in claims:
                issue("unknown_claim", key, c)
        if role in ANALYSIS_ROLES:
            if not p.get("question_ids") or not p.get("claim_ids"):
                issue("unbound_analysis", key, "Analysis needs a question and evidence references")
            if not str(p.get("finding", "")).strip() or not str(p.get("implication", "")).strip():
                issue("missing_reasoning", key, "Finding or business implication is missing")
            evidence = tuple(sorted(set(p.get("claim_ids", []))))
            repeated.setdefault(evidence, []).append(key)
    for q in qi:
        linked = [p for p in pi.values() if q in p.get("question_ids", []) and p.get("role") in ANALYSIS_ROLES]
        if not linked:
            issue("unanswered_question", q, "No substantive analysis page addresses this question")
        decisions = [a for a in ai.values() if a.get("question_id") == q]
        if len(decisions) != 1:
            issue("answer_count", q, "Exactly one consolidated answer or explicit unresolved outcome is required")
    for key, a in ai.items():
        if a.get("question_id") not in qi:
            issue("unknown_question", key, str(a.get("question_id")))
        if a.get("status") not in {"supported", "partial", "refuted", "unresolved"}:
            issue("invalid_answer_status", key, "Answer must reflect evidence outcome")
        if not str(a.get("answer", "")).strip():
            issue("empty_answer", key, "An answer or reason for unresolved status is required")
        supporting = a.get("page_ids", [])
        if not supporting and a.get("status") != "unresolved":
            issue("unsupported_answer", key, "Answered outcome has no supporting page")
        for p in supporting:
            if p not in pi or pi[p].get("role") not in ANALYSIS_ROLES or a.get("question_id") not in pi[p].get("question_ids", []):
                issue("invalid_answer_support", key, p)
    substantive = sum(roles[x] for x in ANALYSIS_ROLES)
    method_count = roles["methods"] + roles["future_research"]
    if method_count >= substantive and method_count:
        issue("plan_dominates", "study", "Method and future-research pages equal or exceed substantive analysis")
    return {
        "status": "structural_gaps" if findings else "structure_checked",
        "semantic_quality": "not_assessed_by_code",
        "counts": {"questions": len(qi), "pages": len(pi), "substantive_pages": substantive, "roles": dict(roles)},
        "findings": findings,
        "reused_evidence_groups": [ids for evidence, ids in repeated.items() if evidence and len(ids) >= 3],
        "next_review": "Read full chapters for evidence support, comparison depth, alternative explanations and specific business answers.",
    }


def register(commands):
    command = commands.add_parser("desk-audit")
    command.add_argument("--study", required=True)


def dispatch(args):
    return audit(json.loads(Path(args.study).read_text(encoding="utf-8")))
