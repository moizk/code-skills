# Root-cause taxonomy: the missing-component lens

A finding is only useful once you name *why* the harness allowed it. "Be more careful" is not a root cause — it is advice the model must remember every time, which means it will fail again. Convert each finding into a **missing component**, because each missing component has a concrete, durable fix.

When the agent fails, ask which piece was absent:

| Missing component | Symptom in the transcript | Durable fix |
|---|---|---|
| **Instruction** | Did the right kind of thing wrong because a rule was never stated | Add a line to CLAUDE.md / a rules file |
| **Source of truth** | Guessed a path/API/convention that exists somewhere unread | Point the agent to the authoritative doc/file; index it |
| **Tool** | Did manually/clumsily what a tool should do; or couldn't act | Add an MCP server / tool, or a script |
| **Validator** | Shipped something a mechanical check would have caught | Add a hook, lint rule, schema check, or test |
| **Permission rule** | Took a risky action it should have paused on; or got prompt-spammed on safe ones | Tune settings.json permissions / approval policy |
| **Context / memory** | Re-asked or re-derived a fact established before, or forgot a preference | Write a memory; improve in-session note-taking |
| **Skill** | Reinvented a multi-step procedure, or the right skill didn't fire | Create a skill, or sharpen an existing skill's description/triggers |
| **Eval** | A regression slipped through with no guard | Add a test fixture / eval case |
| **Recovery path** | Hit an error and flailed instead of recovering cleanly | Document the recovery step; encode it in a skill/runbook |

## The decision order (prefer mechanical over advisory)

For a given finding, walk this ladder and stop at the first that fits — higher rungs are enforced by the system; lower rungs depend on the model remembering:

1. **Mechanical invariant** — a hook, validator, permission rule, or test the harness enforces automatically. Strongest: it cannot be forgotten.
2. **Tool / source-of-truth** — give the agent the capability or the authoritative reference so it *knows* instead of *guesses*.
3. **Skill / subagent** — package a recurring procedure so it runs the same way every time.
4. **Memory / context** — persist a durable fact so it survives across sessions.
5. **Instruction (doc line)** — a rule in CLAUDE.md/rules. Weakest, because it relies on recall; use when the others don't fit.

## Mapping the priority lens (expectation gaps)

Most "the user had to ask again" findings trace to one of:

- **Missing source-of-truth** → the agent guessed instead of reading the spec/design/ticket. Fix: make the artifact discoverable and instruct the agent to read it first.
- **Missing instruction** → an unstated preference/convention. Fix: record it (memory if user-specific, rules if project-wide).
- **Missing process** → built before confirming intent on an ambiguous ask. Fix: instruction to use plan mode / clarify first on under-specified work.
- **Missing validator** → claimed done without proof. Fix: a verification step or test gate before "done."

## Prioritizing the proposals

Rank by **impact × recurrence ÷ effort**:

- **P0** — caused a real bug or an unsafe action, or directly caused a correction round; cheap to fix. Do these first.
- **P1** — recurring inefficiency or a process gap likely to bite again.
- **P2** — sharpening and polish; nice-to-have.

A fix that is enforced (P0 hook/validator) beats five doc lines nobody re-reads.
