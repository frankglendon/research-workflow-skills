# Architecture and engineering decisions

The public package has seven specialist skills plus a coordinator: host-authored study design and six file engines sharing an export boundary. It is designed to make engineering decisions inspectable during a code review or interview.

| Decision | Why | Cost / boundary |
|---|---|---|
| Host agent + skills | Reuse the host's reasoning and tool access without another web platform | Host behavior and permissions vary; no independent task runner |
| Structured plans | Separate proposed business decisions from deterministic file operations | The host must construct and review the plan |
| Input and plan hashes | Detect stale reviews and post-review changes | A hash proves identity, not semantic correctness or reviewer identity |
| Quote membership and numeric checks | Reject fabricated excerpts and some altered numbers | Does not verify web provenance, entailment, units or causality |
| Full review coverage | A missing row cannot silently become a clean row | More review effort; uncertain decisions remain visible |
| No-overwrite export transaction | Validate temporary outputs before publishing final paths | Hard-link publication assumes a compatible local filesystem; a crash can still occur between file and sidecar publication |
| Official Office validation | Reject schema-invalid packages that tolerant viewers may open | Requires .NET and initially available NuGet dependencies |
| Local stage state and dependencies | Resume from committed checkpoints; invalidate downstream completions after upstream changes | Host-driven SQLite module, no background scheduling or authenticated review |
| SkillOpt staging | Separate proposing an edit, evaluating it and applying it | Small decision datasets do not establish broad improvement |

Study design is a host workflow for mixed-method proposals, sampling and analysis plans. Its review checklist does not automatically enforce fieldwork readiness or provide statistical execution.

## Trust and data flow

Source files and source excerpts are data, not instructions. The host forms a plan and performs the task's semantic review. The plan digest covers its complete payload; source file hashes are separately checked against bytes on disk. The engine validates relevant contracts, writes a temporary Office package, normalizes known XML ordering/axis issues, runs the Microsoft validator, checks input hashes again, then publishes the artifact and manifest without overwriting existing files.

The manifest includes input/config/output digests, run ID, counts, engine version and validator status. It excludes source text, translations, answers, filesystem paths and hidden reasoning. Plans retain detailed mappings locally; the public fixture plans contain only synthetic values.

## What a future independent agent would add

A standalone agent would need its own model/tool loop, permissions, budget accounting, retry policy and scheduling around the existing local stage checkpoints. It should call these same contracts and engines. Adding a role prompt or an `agents/openai.yaml` metadata file alone does not provide that runtime.

## Code provenance

The demonstration workflows are a generic public implementation. Shared hash, validation and export utilities were adapted from the author's file-workflow implementation. No employer templates, domain-specific rule sets or private repository history are included. Third-party libraries remain dependencies, not vendored source. AI assistance was used in implementation; claims in this repository are bounded by the executable tests.

## Stage consistency and review scope

`study.py` saves state and its event in one SQLite transaction. Each mutation names the revision it read; an outdated writer must reconcile before retrying. A candidate binds the study token, stage generation, specification, declared execution, input hashes, upstream completion hashes and artifact hashes. Reviews bind that candidate and cover every acceptance ID. File changes, upstream restarts and changed plan dependencies invalidate affected completions.

The state digest detects accidental corruption; it is not a signature. Someone controlling local files can alter the database. `separate_execution` rejects a matching declared builder/reviewer ID but does not authenticate identity or prove separate model execution. The host must supply truthful review evidence. The module gates registered stage completion, while legacy file commands remain usable with their own checks.

`study_eval.py` separates deterministic fixture repetitions from externally graded model or artifact results. It reports observed pass rate, the without-replacement estimate of at least one pass among k, and the estimate of all k passing. The literal all-observed-runs-passed flag is separate. These estimates do not establish performance on unseen tasks.

## Design reference

The stage lifecycle, separation of build/review records and repeated-evaluation approach were informed by [Comet](https://github.com/rpamis/comet/tree/a23a2519ba75060ff9df1fec0e616fbaf63d5a9e). This package implements a smaller Python workflow for research handoffs; it does not vendor, install or run Comet. Comet's native verifier binds trusted runner information; our local host declarations provide a narrower guarantee.
