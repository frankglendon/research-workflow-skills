"""Versioned questionnaire and codebook contracts; no model or network calls."""
import math
import re
from .contracts import GateError, fingerprint

CHOICE = {"single", "dropdown", "multi", "nps", "scale5", "scale0_10", "matrix", "rank"}
TYPES = CHOICE | {"open", "numeric"}
IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")


def need(condition, message):
    if not condition:
        raise GateError(message)


def spec_hash(spec):
    return fingerprint({k: v for k, v in spec.items() if k != "review"})


def require_review(spec):
    review = spec.get("review", {})
    need(review.get("status") == "approved" and review.get("spec_sha256") == spec_hash(spec),
         "Review is missing or belongs to an older specification")
    need(all(review.get(k) is True for k in ("content", "programming", "analysis")),
         "Content, programming and analysis reviews must be complete")


def unique(items, field, label):
    values = [x.get(field) for x in items]
    need(values and all(isinstance(v, (str, int)) and not isinstance(v, bool) and str(v).strip() for v in values),
         f"{label}: missing identifiers")
    need(len(values) == len(set(map(str, values))), f"{label}: duplicate identifiers")
    return {str(v): x for v, x in zip(values, items)}


def validate(spec):
    need(spec.get("schema_version") == 2, "Expected questionnaire schema version 2")
    need(spec.get("meta", {}).get("version"), "A questionnaire version is required")
    need(spec.get("qc_plan"), "Describe the study-specific QC and pilot plan")
    pops = unique(spec.get("populations", []), "key", "Populations")
    objectives = unique(spec.get("objectives", []), "id", "Objectives")
    need(all(o.get("decision") and o.get("metric") for o in objectives.values()), "Objectives need a decision and metric")
    questions = spec.get("questions", [])
    need(questions, "Questions are required")
    need(all(q.get("population") in pops for q in questions), "Undeclared population")
    covered = set()
    for pop in pops:
        need(IDENTIFIER.fullmatch(pop), "Population keys must be portable identifiers")
        qs = [q for q in questions if q["population"] == pop]
        by = unique(qs, "id", "Questions")
        order = {qid: i for i, qid in enumerate(by)}
        for q in qs:
            qid, kind = q["id"], q.get("type")
            need(isinstance(qid, str) and IDENTIFIER.fullmatch(qid) and qid not in {"END", "NEXT"}, "Invalid question ID")
            need(kind in TYPES and q.get("text") and q.get("module"), f"{qid}: unsupported type or missing text/module")
            need(not q.get("loop") and not q.get("derived") and not q.get("piping"),
                 f"{qid}: loops, derived expressions and piping require a separate programming implementation")
            refs = q.get("objective_ids", [])
            need(refs and all(ref in objectives for ref in refs), f"{qid}: objective mapping is incomplete")
            covered.update(refs)
            options = unique(q.get("options", []), "code", qid) if kind in CHOICE else {}
            need(kind in CHOICE or not q.get("options"), f"{qid}: open/numeric questions cannot have options")
            need(all(o.get("label") for o in options.values()), f"{qid}: option labels are required")
            for code, option in options.items():
                need(re.fullmatch(r"[A-Za-z0-9_]+", code), f"{qid}: codes must be portable tokens")
                need(option.get("kind", "normal") in {"normal", "other", "none", "dont_know", "not_applicable"}, f"{qid}: unknown option kind")
                if kind == "multi" and option.get("kind") in {"none", "dont_know", "not_applicable"}:
                    need(option.get("exclusive") is True, f"{qid}: non-substantive options must be exclusive")
                if q.get("randomize") is True and option.get("kind", "normal") != "normal":
                    need(option.get("fixed") is True, f"{qid}: special options need a fixed position")
                if option.get("specify"):
                    need(kind in {"single", "dropdown", "multi"}, f"{qid}: specify is supported for single/multi options")
            if kind in {"nps", "scale0_10", "scale5"}:
                expected = range(1, 6) if kind == "scale5" else range(11)
                need(set(options) == set(map(str, expected)), f"{qid}: incomplete standard scale")
            if kind == "multi":
                lo, hi = q.get("min_selections"), q.get("max_selections")
                need(type(lo) is int and type(hi) is int and 0 <= lo <= hi <= len(options), f"{qid}: invalid selection limits")
            if kind == "rank":
                need(type(q.get("rank_count")) is int and 1 <= q["rank_count"] <= len(options), f"{qid}: invalid rank count")
            if kind == "matrix":
                rows = unique(q.get("rows", []), "code", f"{qid} rows")
                need(all(re.fullmatch(r"[A-Za-z0-9_]+", c) and row.get("label") for c, row in rows.items()), f"{qid}: invalid matrix row")
            if kind == "numeric":
                lo, hi = q.get("min"), q.get("max")
                need(all(type(v) in (int, float) and math.isfinite(v) for v in (lo, hi)) and lo <= hi,
                     f"{qid}: numeric range is required")
            _validate_logic(q, by, order, options)
    need(covered == set(objectives), "Some research objectives have no questions")
    return {"populations": len(pops), "questions": len(questions), "objectives": len(objectives)}


def _validate_logic(q, by, order, options):
    qid = q["id"]
    for rule in q.get("show_if", []):
        need(set(rule) == {"question_id", "codes"}, f"{qid}: unsupported display condition")
        ref = rule["question_id"]
        need(ref in by and order[ref] < order[qid], f"{qid}: display conditions must reference an earlier question")
        need(by[ref]["type"] in {"single", "dropdown", "multi", "nps", "scale5", "scale0_10"}, f"{qid}: unsupported condition type")
        valid = {str(o["code"]) for o in by[ref].get("options", [])}
        need(rule["codes"] and set(map(str, rule["codes"])) <= valid, f"{qid}: unknown condition code")
    seen = set()
    for route in q.get("routes", []):
        need(set(route) == {"codes", "target"} and q["type"] in {"single", "dropdown", "multi", "nps", "scale5", "scale0_10"}, f"{qid}: unsupported route")
        codes = set(map(str, route["codes"]))
        need(codes and codes <= set(options) and not codes & seen, f"{qid}: unknown or overlapping route codes")
        seen |= codes
        target = route["target"]
        need(target == "END" or target in order and order[target] > order[qid], f"{qid}: route must move forward to an existing target")
    need(q.get("default", "NEXT") in {"NEXT", "END"}, f"{qid}: invalid default route")


def variables(spec):
    validate(spec)
    result = []
    for q in spec["questions"]:
        prefix = f'{q["population"]}_{q["id"]}'
        labels = {str(o["code"]): o["label"] for o in q.get("options", [])}
        base = {"population": q["population"], "question_id": q["id"], "label": q["text"],
                "type": q["type"], "values": labels, "base": q.get("show_if", []),
                "missing": "Blank = not asked or missing; keep a separate reason field in collected data."}
        def add(name, **fields):
            result.append({**base, "variable": name, **fields})
        if q["type"] in {"multi", "rank"}:
            for code, label in labels.items():
                if q["type"] == "multi":
                    add(prefix + "_" + code, label=label, values={"0": "Not selected", "1": "Selected"},
                        missing="0 = eligible and not selected; blank = not asked/missing, never silently replace with 0.")
                else:
                    add(prefix + "_" + code, label=label, values={str(i): f"Rank {i}" for i in range(1, q["rank_count"] + 1)},
                        missing="Blank = unranked or not asked; preserve eligibility and missing reason separately.")
        elif q["type"] == "matrix":
            for row in q["rows"]:
                add(prefix + "_" + str(row["code"]), label=row["label"])
        else:
            add(prefix, values=labels if labels else ({"range": [q["min"], q["max"]]} if q["type"] == "numeric" else {}))
        for option in q.get("options", []):
            if option.get("specify"):
                add(prefix + "_other_" + str(option["code"]), label=option["label"] + " — specify",
                    type="open", values={}, base={"question_id": q["id"], "selected": option["code"]})
    unique(result, "variable", "Exported variables")
    mapping = spec.get("variable_names", {})
    need(set(mapping) <= {r["variable"] for r in result}, "Variable name mapping references missing variables")
    for row in result:
        row["canonical_id"] = row["variable"]
        if row["variable"] in mapping:
            row["variable"] = mapping[row["variable"]]
        need(isinstance(row["variable"], str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_.\[\]]*", row["variable"]), "Invalid export variable name")
    unique(result, "variable", "Exported variable names")
    return result


def _selected(answer):
    return {str(a) for a in (answer if isinstance(answer, list) else [answer])}


def simulate(spec, population, answers):
    """Simulate explicit display/forward routes; never interpret prose instructions."""
    validate(spec)
    qs = [q for q in spec["questions"] if q["population"] == population]
    need(qs, "Unknown population")
    order = {q["id"]: i for i, q in enumerate(qs)}
    need(set(answers) <= set(order), "Answers reference unknown question IDs")
    visited, skipped, accepted, edges = [], [], {}, []
    i = 0
    while i < len(qs):
        q = qs[i]; qid = q["id"]
        visible = all(rule["question_id"] in accepted and _selected(accepted[rule["question_id"]]) & set(map(str, rule["codes"]))
                      for rule in q.get("show_if", []))
        if q.get("show_if"):
            edges.append(f"{population}:{qid}:show:{bool(visible)}")
        if not visible:
            skipped.append(qid); i += 1; continue
        need(qid in answers, f"{qid}: a required answer is missing")
        answer = answers[qid]
        _check_answer(q, answer)
        accepted[qid] = answer; visited.append(qid)
        targets = {r["target"] for r in q.get("routes", []) if _selected(answer) & set(map(str, r["codes"]))}
        need(len(targets) <= 1, f"{qid}: answer matches conflicting routes")
        target = next(iter(targets), q.get("default", "NEXT"))
        if q.get("routes"):
            matched = [j for j, r in enumerate(q["routes"]) if _selected(answer) & set(map(str, r["codes"]))]
            edges.extend(f"{population}:{qid}:route:{j}" for j in matched)
            if not matched: edges.append(f"{population}:{qid}:default")
        if target == "END":
            skipped.extend(x["id"] for x in qs[i + 1:]); break
        j = i + 1 if target == "NEXT" else order[target]
        skipped.extend(x["id"] for x in qs[i + 1:j]); i = j
    return {"visited": visited, "skipped": skipped, "edges": edges, "complete": True}


def check_paths(spec):
    required = set()
    for q in spec["questions"]:
        prefix = f'{q["population"]}:{q["id"]}'
        if q.get("routes"):
            required.update(f"{prefix}:route:{i}" for i in range(len(q["routes"])))
            available = {str(o["code"]) for o in q["options"]}
            routed = {str(c) for r in q["routes"] for c in r["codes"]}
            if available - routed or q.get("min_selections") == 0: required.add(f"{prefix}:default")
        if q.get("show_if"):
            required.update(f"{prefix}:show:{v}" for v in (True, False))
    observed = set()
    for case in spec.get("routing_cases", []):
        actual = simulate(spec, case["population"], case["answers"])
        need(actual["visited"] == case["expected_visited"], "Routing test differs from its expected path")
        observed.update(actual["edges"])
    need(required <= observed, "Routing tests do not cover every declared route/default and display branch")
    return {"cases": len(spec.get("routing_cases", [])), "branches": len(required)}


def _check_answer(q, answer):
    kind, qid = q["type"], q["id"]
    opts = {str(o["code"]): o for o in q.get("options", [])}
    if kind in CHOICE - {"matrix", "multi", "rank"}:
        need(type(answer) in (str, int) and str(answer) in opts, f"{qid}: invalid single answer")
    elif kind in {"multi", "rank"}:
        need(isinstance(answer, list) and all(type(a) in (str, int) for a in answer), f"{qid}: expected answer list")
        codes = _selected(answer)
        need(len(codes) == len(answer) and codes <= set(opts), f"{qid}: duplicate or invalid answer")
        if kind == "multi":
            exclusive = any(opts[c].get("exclusive") is True for c in codes)
            need(len(codes) == 1 if exclusive else q["min_selections"] <= len(codes) <= q["max_selections"], f"{qid}: selection limit/exclusivity violation")
        else:
            need(len(answer) == q["rank_count"], f"{qid}: incomplete rank order")
    elif kind == "matrix":
        need(isinstance(answer, dict) and set(answer) == {str(r["code"]) for r in q["rows"]}, f"{qid}: incomplete matrix")
        need(all(type(v) in (str, int) and str(v) in opts for v in answer.values()), f"{qid}: invalid matrix value")
    elif kind == "numeric":
        need(type(answer) in (int, float) and math.isfinite(answer) and q["min"] <= answer <= q["max"], f"{qid}: out-of-range numeric answer")
    else:
        need(isinstance(answer, str) and answer.strip(), f"{qid}: empty open answer")


def draft_codebook(spec):
    return {"schema_version": 1, "version": spec["meta"]["version"], "questionnaire_sha256": spec_hash(spec),
            "variables": variables(spec), "codeframes": [], "review": {"status": "draft"}}


def validate_codebook(spec, codebook):
    need(codebook.get("schema_version") == 1 and codebook.get("version"), "Unsupported codebook schema or missing version")
    need(codebook.get("questionnaire_sha256") == spec_hash(spec), "Codebook belongs to an older questionnaire")
    expected = variables(spec)
    need(codebook.get("variables") == expected, "Variable dictionary differs from the current questionnaire; regenerate it")
    open_questions = {(q["population"], q["id"]) for q in spec["questions"] if q["type"] == "open"}
    frames = codebook.get("codeframes", [])
    seen = set()
    for frame in frames:
        key = (frame.get("population"), frame.get("question_id"))
        need(key in open_questions and key not in seen, "Codeframes require unique, existing open questions")
        seen.add(key)
        need(frame.get("unit") in {"response", "meaning_unit"} and frame.get("mode") in {"single", "multi"}, "Declare coding unit and multiplicity")
        codes = unique(frame.get("codes", []), "code", "Codeframe")
        for code, item in codes.items():
            need(all(isinstance(item.get(k), str) and item[k].strip() for k in ("label", "definition", "include", "exclude")),
                 "Every code needs a label, definition, inclusion and exclusion rule")
            if item.get("special"):
                need(item.get("exclusive") is True, "Special response codes must be exclusive")
            ancestors, parent = {code}, item.get("parent")
            while parent is not None:
                parent = str(parent)
                need(parent in codes and parent not in ancestors, "Invalid codeframe hierarchy")
                ancestors.add(parent); parent = codes[parent].get("parent")
    return {"variables": len(expected), "codeframes": len(frames)}
