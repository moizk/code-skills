# Report template

Keep it tight and evidence-backed. Findings ordered by impact; end with a numbered apply-list and a question. Scale length to the session — a clean run gets a short report, not padding.

```markdown
# Session Retrospective — <date> · <branch> · <one-line goal>

## Scorecard
- **Outcome:** <shipped / partial / abandoned> — <one line>
- **Rounds to get there:** <N user prompts for this task> <note if rework-heavy>
- **Tool errors:** <count> · **File rework:** <files churned> · **Cache hit ratio:** <ratio>
- **Skills / subagents used:** <list or "none">
- **Headline:** <the single most important thing to improve, or "clean run — minor sharpening only">

## Findings

### [P0] <short title>
- **What happened:** <one or two sentences>
- **Evidence:** <tool error / user correction / metric> (record `<uuid>` or the user's words)
- **Root cause (missing component):** <instruction | source-of-truth | tool | validator | permission | memory | skill | eval | recovery>
- **Proposed fix:** <concrete change>
- **Where it lands:** <CLAUDE.md | rules/<file> | memory | skill <name> | settings.json hook/permission | test | workflow habit>
- **Effort:** <low | medium | high>

### [P1] <short title>
<same shape>

### [P2] <short title>
<same shape>

## What went well
<1–3 bullets — reinforce the habits worth keeping. Always include this; a retro is not only a defect list.>

## Apply list
1. <fix> → <target>
2. <fix> → <target>
3. <fix> → <target>

Which of these should I apply? I can do all, a subset, or none — and I'll write a copy of this retro to `.claude/tmp/retrospectives/<date>-<slug>.md` so the lessons carry forward.
```

## Notes on writing it well

- Lead with the **headline** — the one change with the highest payoff. Don't bury it under minor items.
- Tie every P0 to either a real bug/unsafe action or a correction round. If a finding can't be traced to evidence, cut it.
- Phrase fixes as the *delta* to apply, not a lecture. "Add to rules/testing.md: run the full suite before reporting done" beats "you should test more."
- Prefer one strong enforced fix over five doc lines.
- If the session was genuinely clean, say so plainly and keep the report to the scorecard, "what went well," and one or two sharpening ideas.
