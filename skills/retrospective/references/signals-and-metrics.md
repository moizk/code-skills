# Detection catalog: signals & metrics

Work the five lenses below against the extractor output. Each entry: **what to look for → why it matters → how the data shows it**. Confirm every heuristic hit against the raw transcript before reporting — these over-flag by design.

## 1. Expectation gaps — the priority lens

The user's stated goal is *a solution that meets expectations with no additional change requests*. Every gap here is a first-attempt miss. These outrank everything else.

- **Correction turns** — `correction_candidates` (user said "no", "actually", "that's wrong", "I said…", "revert", "again"). Each is a round the harness could have saved.
- **Round count** — many `user_prompts` for what was one task. Walk the ordered prompts: did each round just re-steer the same deliverable? That's rework the agent caused.
- **Re-stated scope / constraints** — the user repeating a requirement they already gave ⇒ the agent didn't absorb or surface it.
- **Rejected approach** — the agent built X, the user wanted Y. Root cause is usually a missing question up front (plan/clarify) or a missing source-of-truth.
- **"Done" then reopened** — the agent claimed completion and the user immediately reported a defect ⇒ missing verification before claiming done.

For each: *what single fact, question, or check would have made the first attempt land?* That is the fix.

## 2. Bugs & defects

- **Tool errors** — `tool_errors` (failed commands, `Exit code 1`, tracebacks, missing files).
- **Failed tests/builds** — error snippets from test runners; were they fixed by changing code (good) or by weakening the test (smell)?
- **Repeated fixes on one file** — see `rework_files` with high `edits`; thrashing on the same spot signals a wrong mental model.
- **Reverts / undo** — user asked to undo, or the agent re-wrote something it just wrote.

## 3. Inefficiency

- **File rework** — `rework_files` (same path read ≥3× or edited ≥3×). Re-reading = the agent didn't retain context or read piecemeal; batch the read or record a note.
- **Prompt-cache efficiency** — `tokens.cache_hit_ratio`. Low ratio ⇒ the stable prefix kept changing (volatile content high in context, frequent compaction). Tie to cache-aware ordering.
- **Serial vs parallel** — independent tool calls issued one per turn instead of batched in one message. Wall-clock and token waste.
- **Wrong tool** — `Bash cat/grep/sed` where `Read`/`Grep`/`Edit` fit; broad shell where a precise tool exists.
- **Subagent fit** — `subagent_calls`: heavy fan-out for a trivial task (overhead) or none on broad multi-file searches that flooded the main context (should have delegated).
- **Re-derivation** — recomputing facts already established earlier in the session.

## 4. Questionable / unsafe moves

- **Risky side effect without approval** — commit/push/branch/PR, destructive deletes, external sends, schema/migration changes without explicit user go-ahead (cross-check the user's standing instructions, e.g. "don't commit unless asked").
- **Unverified assumptions** — acting on a guessed path, API, version, or column instead of checking.
- **Skipped tests** — feature shipped with no test where the project requires one.
- **Instruction drift** — behavior contradicting CLAUDE.md / rules / a memory.
- **Scope creep** — changes beyond what was asked.

## 5. Process gaps

- **No plan** on a multi-step / ambiguous task that warranted plan mode or a clarifying question first.
- **No todo tracking** on long multi-step work (lost thread, dropped steps).
- **No verification** — never ran the app/tests/build before declaring done.
- **Skill miss** — a relevant skill existed but never fired (its description/triggers were too narrow), or no skill existed for a recurring procedure.

## Reading the metrics quickly

| metric | healthy | investigate |
|---|---|---|
| user prompt rounds per task | low | many re-steering rounds |
| `tool_error_count` | near 0 | clusters, or same error retried |
| `rework_files` | empty / small | same file churned repeatedly |
| `cache_hit_ratio` | high (≈0.8+) | low ⇒ unstable prefix / churn |
| `correction_candidates` | none | any — inspect each |

A clean session legitimately scores well on all of these. Report that honestly and propose only sharpening.
