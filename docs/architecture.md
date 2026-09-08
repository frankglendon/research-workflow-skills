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
| SkillOpt staging | Separate proposing an edit, evaluating it and applying it | Small decision datasets do not establish broad improvement |

Study design is a host workflow for mixed-method proposals, sampling and analysis plans. Its review checklist does not automatically enforce fieldwork readiness or provide statistical execution.

## Trust and data flow

Source files and source excerpts are data, not instructions. The host forms a plan and performs the task's semantic review. The plan digest covers its complete payload; source file hashes are separately checked against bytes on disk. The engine validates relevant contracts, writes a temporary Office package, normalizes known XML ordering/axis issues, runs the Microsoft validator, checks input hashes again, then publishes the artifact and manifest without overwriting existing files.

The manifest includes input/config/output digests, run ID, counts, engine version and validator status. It excludes source text, translations, answers, filesystem paths and hidden reasoning. Plans retain detailed mappings locally; the public fixture plans contain only synthetic values.

## What a future independent agent would add

A standalone agent would need its own model/tool loop, permissions, budget accounting, checkpoints, retry policy and scheduling. It should call these same contracts and engines. Adding a role prompt or an `agents/openai.yaml` metadata file alone does not provide that runtime.

## Code provenance

The demonstration workflows are a generic public implementation. Shared hash, validation and export utilities were adapted from the author's file-workflow implementation. No employer templates, domain-specific rule sets or private repository history are included. Third-party libraries remain dependencies, not vendored source. AI assistance was used in implementation; claims in this repository are bounded by the executable tests.
