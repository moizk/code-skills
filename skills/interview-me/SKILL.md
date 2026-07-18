---
name: interview-me
description: Extracts what the user actually wants vs. what they think they should ask for, via a one-question-at-a-time interview until ~95% confidence in the underlying intent. Use when an ask is underspecified ("build me X" with no who/why/success), when the user invokes it ("interview me", "grill me", "are we sure?", "stress-test this"), or when you catch yourself silently filling in ambiguous requirements before any plan, spec, or code exists. Not for unambiguous self-contained asks (renames, typos, factual questions), when the user wants speed over verification, or in non-interactive runs.
---

# Interview Me

What people ask for and what they want diverge. They say "a dashboard" because that's the conventional ask, not because it solves their problem. The cheapest moment to close that gap is before any plan, spec, or code exists — afterward, switching costs are real and the user rationalizes the wrong thing into "good enough." This skill produces a **confirmed statement of intent** that downstream skills (spec, planning, idea-refine) consume.

## When to use

- The ask is missing at least one of: **who** it's for, **why** now, what **success** looks like, the binding **constraint**.
- The request is conventional rather than specific ("build me X", "make it faster") and you'd have to guess to proceed.
- Two reasonable values are in tension (simplicity vs. flexibility, cost vs. speed) and the user hasn't said which wins.
- The user explicitly invokes it.

**Don't use** for unambiguous, self-contained asks (rename, typo, "how does X work?"), when the user asked for speed over verification, or when you already have ≥95% confidence.

**Never use in non-interactive contexts** (CI, scheduled runs, `/loop`, autonomous loops). If the ask is underspecified there, flag it as a blocker instead of guessing.

## Process

**1. Hypothesize with a confidence number.** Before asking anything, write your best read in one sentence plus an honest 0–100%. Below ~70%, append what's still missing.
```
HYPOTHESIS: You want to answer "how are we doing?" in standup; "dashboard" was just the convention that surfaced.
CONFIDENCE: ~30% — missing: who it's for, what "metrics" means, what success looks like
```
If you can't predict the user's reactions to your next three questions, the number is too high.

**2. Ask one question at a time, each with a guess attached.** Wait for the reaction before the next.
```
Q:     <one focused question>
GUESS: <your hypothesis for the answer, plus the reasoning behind it>
```
One at a time, not batched: the user can't react to a buried hypothesis, and question 3 often depends on answer 1. The guess makes the user react (faster than generating from scratch) and exposes your assumptions. Risk: a polite user agrees to be agreeable — mitigate by being visibly willing to be wrong, and sometimes guess in a direction you expect pushback on.

**3. Catch "want vs. should-want."** Distrust answers that pattern-match best practice ("scalable", "clean", "the standard approach") or hedge ("I should probably…", "I'm supposed to…"). When you hear them, ask:
> "If you didn't have to justify this to anyone, what would you actually want?"

**4. Restate intent in their words** (5–8 lines, confirmable line by line):
```
- Outcome:      <one line>
- User:         <who benefits>
- Why now:      <what changed>
- Success:      <how we know it worked>
- Constraint:   <the binding limit>
- Out of scope: <what we're explicitly NOT doing>

Yes / no / refine?
```
The "Out of scope" line is non-negotiable — silent disagreement about non-goals is half of misalignment.

**5. Require an explicit yes.** Not a yes: "whatever you think" (delegation → re-ask with two concrete options), "sounds good"/"sure let's go" (ask "anything you'd refine?"), or silence. Fold in corrections and restate until you get a real yes.

## Stop condition (~95%)

Done when you can answer yes to: **Can I predict the user's reaction to the next three questions I'd ask?** If yes, stop and restate. If no, ask the next question. Floor: if several rounds pass and you still can't predict, say so — "I've asked X questions and still can't predict your reactions; something foundational is missing. Want to step back?" — rather than grinding.

## Output

A confirmed statement of intent (the Step 4 restate + an explicit yes). Specs, plans, and tasks are downstream. If the intent must persist (multi-session work, a handoff), offer to save it to `docs/intent/[topic].md` — only after the user confirms.

## Validation

Before treating the intent as confirmed, check:
- [ ] First turn stated a hypothesis with a confidence number (reason attached if <~70%).
- [ ] Questions came one at a time, each with a guess attached.
- [ ] The "what would you actually want if you didn't have to justify it?" probe ran on any best-practice/convention-signaling answer.
- [ ] A concrete restate (Outcome / User / Why now / Success / Constraint / Out of scope) was written back.
- [ ] The user gave an explicit yes — not "whatever you think", "sounds good", or silence.

## Red flags

- Three+ questions in one message (batching, not interviewing).
- A question with no hypothesis attached (surveying, not committing).
- Accepting "whatever you think is best" as terminal.
- Producing a spec/plan/task list before the explicit yes.
- Questions framed as "what's best practice?" instead of "what do you actually want?".
- Accepting "scalable/clean/modern" without probing what it concretely means.
- Confidence not rising across three rounds (wrong questions — reframe).
- Skipping "Out of scope", or saving the intent doc before the user said yes.
