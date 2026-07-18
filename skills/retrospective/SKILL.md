---
name: retrospective
description: "Run a retrospective on the current (or a past) Claude Code session — load the full transcript, analyze what actually happened, and propose concrete harness improvements that prevent bugs, remove questionable/unsafe moves, cut wasted work, and raise the odds the next solution meets the user's expectations on the first try with no follow-up change requests. Use when the user asks to reflect on, review, post-mortem, debrief, or learn from a session or how the agent worked; to figure out why a task needed several rounds of corrections; or to turn this session's lessons into durable rules, memories, skills, subagents, hooks, permissions, or evals. Triggers on 'retrospective', 'retro', 'post-mortem', 'debrief', 'what went wrong this session', 'how could you have done this better', 'reflect on this session', 'capture lessons', 'why did that take so many tries'. Grounded in modern agentic engineering practice and Claude Code's native feature set."
metadata:
  version: "1.0.0"
  scope: "session-analysis-and-harness-improvement"
---

# Retrospective

Turn a finished (or in-progress) Claude Code session into compounding improvement. Read the real transcript, find where the run leaked quality — bugs, unsafe or questionable moves, wasted effort, and above all moments where the user had to ask again because the first result missed the mark — root-cause each one, and propose the smallest durable change to the harness that stops it recurring.

This is a **feedback-loop skill**. Its product is not a recap; it is a short list of concrete, routed, prioritized changes the user can apply. The north star is the user's own goal: **a solution that meets expectations with no additional change requests.** Every correction round in a transcript is evidence the harness let the model guess instead of know — find the missing piece and encode it.

## Operating principles

- **Evidence over vibes.** Every finding cites a real moment (a tool error, a user correction, a metric). No invented problems. If the session went well, say so and propose only high-value sharpening.
- **Ground the analysis in data, not the raw transcript.** Run the extractor script; reason over its structured output. Pull raw excerpts only for moments you need to inspect closely. This keeps the analysis cheap and avoids dragging an entire chain-of-thought back into context.
- **Never expose hidden reasoning.** The extractor deliberately omits raw `thinking`. Report *behavior and outcomes*, not the model's private reasoning. Cite tool calls and user messages as evidence.
- **Root-cause, don't moralize.** "Be more careful" is not a fix. For each finding name the *missing harness component* (instruction, source-of-truth, tool, validator, permission rule, context/memory, skill, eval, recovery path) and the concrete artifact that closes it.
- **Propose first, apply on approval.** Improvements touch high-impact surfaces (CLAUDE.md, rules, memory, skills, settings/hooks). Present the report, let the user pick, then apply each chosen item through its proper mechanism. Never auto-edit the global harness.
- **Smallest durable fix wins.** Prefer a mechanical invariant (hook, validator, permission) over a doc line, and a doc line over "try harder." A fix that the harness enforces beats advice the model must remember.

## Procedure

### 1. Locate and extract the session

Default target is the **current** session. Run the extractor from the project's working directory:

```bash
python3 ~/.claude/skills/retrospective/scripts/analyze_session.py
```

It auto-selects the newest transcript for the current cwd and prints a structured JSON summary (tools used, skills invoked, genuine user prompts, tool errors, file rework, token/cache metrics, correction candidates). Useful flags:

- `--list` — show available transcripts, newest first.
- `--file PATH` / `--session ID` — target a specific session.
- `--skip-newest` — use the second-newest (when *this* retrospective run is itself the newest file and you want the session before it).
- `--cwd DIR` — analyze a session from a different project.

If the user says "the last session" / "what I did before this," the newest file is the current run — use `--skip-newest`. For cross-session patterns, run `--list` and analyze the relevant files. See [references/transcript-format.md](references/transcript-format.md) for the JSONL schema and how to grep the raw file for a specific `uuid` when you need detail the summary doesn't carry.

### 2. Reconstruct the run

From the extractor output, write (for yourself) a one-paragraph timeline: what the user asked, how many genuine prompt rounds it took, which skills/subagents ran, what the outcome was. The **user_prompts** list in order is the spine — count the rounds. Many rounds for one task = the headline problem.

### 3. Detect signals

Work through the detection catalog in [references/signals-and-metrics.md](references/signals-and-metrics.md). The five lenses, highest-value first:

1. **Expectation gaps** (the priority) — `correction_candidates`, repeated/rephrased asks, rejected approaches, scope the user had to re-state. Each one means the first attempt missed. Ask: *what would the agent have needed to know up front to get it right the first time?*
2. **Bugs & defects** — `tool_errors`, failed tests/builds, reverts, repeated fix attempts on one file.
3. **Inefficiency** — `rework_files` (re-reading/re-editing the same file), low `cache_hit_ratio`, serial tool calls that could have been parallel, oversized context, wrong tool choice, over/under-use of subagents, re-deriving already-known facts.
4. **Questionable / unsafe moves** — risky side effects without approval, unverified assumptions, skipped tests, ignored CLAUDE.md / rules, scope creep beyond the ask.
5. **Process gaps** — no plan on a multi-step task, no todo tracking, no verification step before claiming done.

Confirm each candidate against the raw transcript before reporting it — heuristics over-flag. Drop anything you can't back with evidence.

### 4. Root-cause each finding

For every confirmed finding, identify the **missing component** using the framework in [references/improvement-taxonomy.md](references/improvement-taxonomy.md): missing instruction, source-of-truth, tool, validator, permission rule, context/memory, skill, eval, or recovery path. The fix follows from the gap.

### 5. Route each fix to the right surface

Map the fix to a concrete Claude Code mechanism — see [references/claude-code-capabilities.md](references/claude-code-capabilities.md):

- Durable rule / preference → **CLAUDE.md** or a file in **rules/**.
- Durable fact about the user/project/feedback → **memory** (`~/.claude/projects/<slug>/memory/` + `MEMORY.md`), following the memory spec.
- Recurring multi-step procedure → a new or sharpened **skill** (tighten the *description/triggers* if the skill existed but didn't fire).
- Specialized delegated work → a **subagent** (or guidance on when to delegate).
- Mechanical invariant (auto-format, block a footgun, reduce permission prompts) → **settings.json hooks / permissions**, applied via the `update-config` skill.
- Missing capability → an **MCP server / tool**.
- Regression guard → an **eval / test fixture**.
- Better in-session habit → a **workflow note** (plan mode, TodoWrite, parallel calls, `/code-review` before done).

### 6. Write the report

Produce the report from [references/report-template.md](references/report-template.md): a scorecard, then findings ranked by impact, each with evidence → root cause → proposed fix → target surface → effort. End with a prioritized, numbered apply-list and ask which items to apply.

### 7. Apply on approval & close the loop

For each approved item, apply it through its proper mechanism (edit CLAUDE.md/rules, write a memory + MEMORY.md pointer, scaffold/sharpen a skill, invoke `update-config` for settings, add an eval). Re-run any test you added. Then, unless the user opts out, write a durable artifact to `.claude/tmp/retrospectives/<YYYY-MM-DD>-<slug>.md` (create the dir if needed) so lessons accumulate across sessions — that persistence *is* the compounding feedback loop this skill exists to create.

## Guardrails

- Read-only until the user approves changes. The analysis never edits the harness on its own.
- Do not quote or paraphrase raw chain-of-thought; reason from actions and results.
- Be proportionate: a clean session gets a short, honest report, not manufactured findings.
- A transcript shows what the model did, not always why — when intent is ambiguous, say so and ask rather than assert a root cause.
- Don't restate what the repo/CLAUDE.md already enforces. Propose only the delta.
