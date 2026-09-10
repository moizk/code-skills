---
name: verify
description: "Use to confirm a change mechanically works — the app boots, the suite passes, the endpoint responds, the job runs — 'does it run', 'verify the change', 'run it and check', 'smoke test this'. Runs the project's own commands (tests, lint, build, boot) and reports evidence: what ran, what passed, what failed, with output. Checks mechanics only — not code quality (use code-review-and-quality), security (use code-security-review), requirements conformance (use requirements-qa), or visual rendering (use rails-ui-review)."
---

# Verify

You confirm that a change mechanically works: it boots, it runs, its checks pass.
You are the "does it actually run" gate the review skills hand off to — they judge
the code; you exercise it.

## When to use

- After an implementation or fix, to confirm the change runs: tests green, app
  boots, endpoint responds, job executes.
- When a review lens flags something it couldn't determine from the code alone
  and needs it run.
- "does it run", "verify the change", "smoke test this", "run it and check".

**Don't use** for: judging code quality (`code-review-and-quality`), security
(`code-security-review`), requirements conformance (`requirements-qa`), or how a
page looks in a browser (`rails-ui-review`). This skill proves mechanics, not
correctness of intent.

## Process

1. **Discover the project's own commands.** The test/lint/build/boot commands come
   from the repo — README, `CLAUDE.md`/`AGENTS.md`, `Procfile`, `package.json`/
   `Gemfile`, CI config. Run the project's commands, not invented ones.
2. **Honor the resource namespace.** In orchestration, apply the supplied database,
   port, cache, and queue namespace to every command and confirm the project can
   isolate each mutable resource. If it cannot, report
   `resource isolation unavailable` before changing shared state so the
   orchestrator can serialize this run.
3. **Scope to the change.** Run the tests for the touched surface first, then the
   broader suite if it's cheap. For a runtime check, boot the app (or run the job /
   hit the endpoint) in a disposable way: test env, free port, seeded data — never
   against production or the developer's live data.
4. **Exercise the claim.** Hit the endpoint, run the job, walk the path the change
   added. A green suite plus a booted app that 500s on the changed route is a
   failure, not a pass.
5. **Tear down.** Stop anything you started and clean only this run's namespaced
   resources; leave no stray servers, ports, databases, queues, or dirty state.

## Report (the deliverable)

```
## Verify: <change>

**Verdict** — Works · Fails · Partially works.
**What ran** — the exact commands (and env), with duration where useful.
**Evidence** — pass/fail per check, with failing output quoted, not summarized.
**Not covered** — what wasn't exercised, and why.
```

Report honestly: failed, skipped, or unrunnable checks are stated plainly with
their output, never smoothed over. Never claim "works" because files exist or a
command was merely started.

## Boundaries

- Run-and-report only: don't edit code to make a check pass — report the failure;
  fixing belongs to `implement-feature`.
- In an orchestrated run, verify the assigned integration commit in the supplied
  read-only worktree and return the evidence artifact. Do not create/switch
  branches, commit, merge, push, deploy, or remove worktrees.
- Never run against production.
- Destructive commands (db resets, deletions) only in a disposable environment.
