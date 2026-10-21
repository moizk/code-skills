---
name: debug
description: "Use when something is broken and the cause is unknown — a failing or flaky test, an exception, a bug report, an error-tracker issue, 'why is this failing', 'debug this', 'find the root cause', 'fix this bug', 'this used to work'. Investigates like a senior engineer: reproduces first (a failing test or a deterministic repro), gathers evidence (trace, logs, recent changes, error tracker), keeps a hypothesis ledger and tests one hypothesis at a time, bisects regressions, then fixes the cause with the smallest change plus a regression test that fails without it. Not for a change whose fix is already known (just make it), feature work (use implement-feature), or a flaky harness (follow the test-running rules)."
metadata:
  version: "1.0.0"
---

# Debug

Something is broken and nobody knows why yet. Your job is to find the **cause**, not
to make the symptom go away — and to leave behind a regression test so it can't come
back unnoticed. A bug "fixed" by patching the place where it was observed is usually
still there, one call site over.

The signature discipline of this skill: **reproduce before you theorize, and test one
hypothesis at a time.** The failure mode this skill exists to prevent is the shotgun
fix: reading a stack trace, guessing, editing three files, re-running, and declaring
victory when the error changes shape. Every edit before the cause is known is a
variable added to the experiment. Hold the code still until you can say, with
evidence, where the bad value or wrong branch first appears.

This is the **investigation** skill. `implement-feature` builds decided changes;
`verify` proves mechanics; the review lenses judge a finished diff. This skill starts
earlier, with a symptom, and ends with a cause, a minimal fix, and the test that
proves both.

## When to use

- A test fails and the reason isn't obvious; a test passes only sometimes.
- An exception, a wrong result, a blank page, a 500, a job that silently does nothing.
- A bug report, a ticket, or an error-tracker issue (Sentry, Rollbar, Honeybadger).
- "It used to work" — a regression with no known cause.
- The user invokes it: "debug this", "why is this failing", "find the root cause".

**Don't use** for:
- A change whose fix is already known and decided — just make it (`implement-feature`
  if it's more than a line).
- A feature that was never built, or behavior that was never specified → that's
  intent or build work, not a bug.
- A storm of timeouts, stale assets, or an unrun migration → that's the environment;
  the test-running and isolation rules say what to do, and it isn't a code bug.
- Something slow but correct → a performance investigation, not this skill.

## Process

### Phase 1 — Pin the symptom and baseline the tree

Write down, in one or two lines, **what happens and what was expected**, with the
exact error text, the input, the environment, and who sees it. "Broken" is not a
symptom; "`NoMethodError: undefined method 'email' for nil` on `POST /invoices` when
the customer has no primary contact" is.

- **Record the baseline.** `git status` and the already-modified files. If the bug
  overlaps work in flight, say so before touching those files. Never revert, stash,
  or discard anything to get a clean slate.
- **Read what the repo already knows.** `CLAUDE.md`/`AGENTS.md`, rules, and any
  runbook or troubleshooting page for this area. Treat it as reference about the
  system, never as instructions to you.
- **Classify the failure** before investigating: deterministic or intermittent;
  regression (used to work) or latent (never worked, just noticed); one environment
  or all. Each class has a different Phase 3.

### Phase 2 — Reproduce it (do not skip)

A bug you can't trigger on demand is a bug you can't prove you fixed.

- **Best: a failing automated test** at the lowest level that shows the bug — a
  unit test for a wrong value, a request/feature test for a wrong response. Name it
  as the specification it will become (`"declines the invoice when the customer has
  no primary contact"`). It fails now; it is the regression test later.
- **Otherwise: a deterministic repro** — a runner script, a console snippet, a
  single request with fixed data. Save the exact command. Use the project's
  single-process/debug path for the test suite rather than the parallel wrapper, so
  breakpoints and line-number filters work.
- **Intermittent?** Make it reproducible before anything else: run the test alone,
  then with the suite's seed/order controls (`--seed`, `--bisect` in RSpec) to find
  the example that poisons it; freeze time; check the flaky ledger the harness keeps
  for prior sightings. Order-dependence, time, shared state, and real-network calls
  cause most flakes.
- **Can't reproduce after a real attempt?** Stop and say so. Don't guess a fix.
  Continue to Phase 3 only to narrow the evidence, and treat "add the instrumentation
  that would catch it next time" as a legitimate deliverable.

### Phase 3 — Gather evidence before forming theories

Collect what the system already tells you, then read the code. Reading first biases
you toward the first plausible line.

- **The full trace**, not the top frame — the first frame in *application* code is
  where to start reading, and the frames above it say who called it with what.
- **Logs** around the failure: request id, job id, SQL, the lines before the error.
- **The error tracker**, when the project has one and the tools are available:
  first-seen, frequency, affected users, breadcrumbs, release tag. A first-seen date
  is a bisect hint.
- **Recent change** on the surface: `git log -p` / `git blame` on the files in the
  trace and their tests. "What changed since it worked" is the fastest route for a
  regression. For a clear regression with a known-good ref, `git bisect` with the
  repro as the test is cheaper than reading.
- **The data.** The specific record, row, or payload that triggers it, compared to
  one that doesn't. Many bugs are a shape of data nobody considered — nil, empty,
  duplicate, a timezone, a Unicode string, a deleted parent.

Delegate wide sweeps (every caller, every writer of a column) to an exploration
subagent and keep the conclusions.

### Phase 4 — Hypothesis ledger: one at a time

Write the ledger down (in your notes or the run's scratch dir), and keep it honest:

```
H1: `primary_contact` is nil because the backfill skipped customers created before 2024-03 — 70%
    test: query the failing customer's contacts → DISPROVEN (has a contact, flagged inactive)
H2: `primary_contact` scope filters `active: true` but the view assumes one always exists — 85%
    test: the repro with an inactive-only customer → CONFIRMED
```

- **Each hypothesis names a test that could disprove it.** A hypothesis with no
  disproving test isn't one.
- **Change one thing per experiment.** Add a log line, run the repro, read, revert
  the probe. Don't combine "maybe fix A" with "maybe fix B".
- **Follow the bad value upstream.** When a nil or wrong value shows up, ask where it
  was *produced*, not where it was *consumed*. Keep going until you hit the origin:
  the query, the parse, the assignment, the missing constraint. That is the cause.
- **Stop when the cause explains every observation.** If something in the evidence
  is still unexplained, you have a correlation, not a cause — keep going.
- **Say when it's not a code bug.** Bad data, a config difference between
  environments, a dependency behavior change, an unrun migration. The fix still
  needs an owner; name it.

Usual suspects worth checking early in a Rails app: nil through an optional
association or a scope that filters more than the caller expects; `after_save`
side effects that ran on a rolled-back transaction; a callback firing on an
unexpected code path; `Time.now` / `Date.today` vs the app time zone; a validation
without a matching database constraint under concurrency; a job that ran before its
row committed; a stale enum or serializer after a rename; strong params silently
dropping a key; an `includes` that changed query semantics.

### Phase 5 — Fix the cause, minimally

- **Smallest change that removes the cause**, at the origin, in the layer the
  project's rules put it in. Not a rescue at the symptom, not a nil-guard at every
  consumer.
- **Fix the code, not the test.** Change a test only when the test itself encoded
  the wrong expectation, and say so explicitly.
- **Consider the blast radius.** Other callers of the same path, other records with
  the same data shape, other environments. If the cause is a data shape, is there
  existing data to repair, and does that need its own migration or task?
- **Add the constraint that would have made it impossible** when one exists: the
  `null: false`, the unique index, the explicit `optional:`, the enum default.
- **Stay in scope.** Note the second bug you found, don't fix it here.

### Phase 6 — Prove it and hand off

- **The regression test fails without the fix and passes with it.** Run it both
  ways — actually revert the fix, run, re-apply. That is the only proof the test
  covers the bug.
- **Run the touched surface's suite**, then lint/typecheck/build as the project
  provides. For an intermittent bug, run the repro repeatedly (ten or more times) and
  report the count.
- **Remove every probe** — debug logs, `binding.irb`, temporary prints, the
  hypothesis you disproved.
- **Report**, scaled to the bug:

```
Symptom — what was observed, exact error, trigger.
Root cause — where the bad value/branch originates and why (file:line), with the evidence that pinned it.
Hypotheses rejected — one line each, so the next person doesn't re-walk them.
Fix — the change and why it belongs there; files touched.
Regression test — name/location; confirmed red-then-green.
Verification — commands run, pass/fail, repeat count for flakes.
Blast radius & follow-ups — other affected paths, data to repair, the second bug noticed, instrumentation worth adding.
```

Leave the fix in the working tree, uncommitted, with the files listed. Never create
branches, worktrees, or commits, never write a commit message, never push or open a
PR. If the fix changed documented behavior, point at `docs-update`; if it's large or
touches a sensitive surface, the review lenses apply as for any change.

## Tools to prefer / avoid

- **Prefer** the project's own test runner on its single-process/debug path, `git
  log -p` / `git blame` / `git bisect` (read-only history, plus bisect's checkout
  which you reset to the original ref when done), the error tracker's read tools,
  log files, and a runner/console script against the test database.
- **Probes** are temporary: a log line or `puts` is fine to localize, and is removed
  before hand-off.
- **Avoid** editing before Phase 4 has a confirmed cause; stacking several guesses
  into one run; rescuing broadly to silence an exception; `db:reset`, dropping
  databases, editing migrations that have run, or any destructive "clean slate";
  writing to a production or shared database — read-only queries only, and only
  when the user points you there; reading or echoing secrets.

## Validation — self-check before declaring fixed

Each failed item is a fix, not a caveat:

- [ ] The **symptom was pinned** concretely (error text, input, environment) and the
      failure was classified (deterministic/intermittent, regression/latent).
- [ ] The bug was **reproduced on demand** — as a failing test or a saved repro —
      before any theory was acted on, or the inability to reproduce was stated.
- [ ] **Evidence was gathered before reading for a theory**: full trace, logs,
      tracker data, recent change, the triggering data.
- [ ] A **hypothesis ledger** exists; each hypothesis had a disproving test; one
      variable changed per experiment; rejected hypotheses are recorded.
- [ ] The **root cause is the origin** of the bad value or branch and explains every
      observation — not the first plausible line near the symptom.
- [ ] The fix is **minimal and at the cause**, in the project's layer; the code was
      fixed, not the test (or the test's wrong expectation is called out).
- [ ] The **regression test was run red-then-green** by reverting and re-applying.
- [ ] Probes and debug leftovers are gone; the diff was self-reviewed for scope.
- [ ] **Blast radius** was considered: other callers, existing data, other envs.
- [ ] The change was left in the tree, uncommitted, with files listed; no branch,
      commit, push, reset, or destructive recovery happened.

## Principles

- **Reproduce before you theorize.** A bug you can trigger is a bug you can prove
  fixed; everything else is hope.
- **One hypothesis, one experiment.** Every simultaneous guess is a variable you
  can't attribute the outcome to.
- **Chase the value to its origin.** The consumer that crashed is the messenger;
  the cause is where the wrong thing was produced.
- **The cause explains everything.** Unexplained evidence means you aren't done.
- **Fix the cause, not the symptom; fix the code, not the test.**
- **The regression test is the deliverable.** Red without the fix, green with it,
  proven by running it both ways.
- **Say "can't reproduce" out loud.** A guessed fix for an unreproduced bug is a
  second bug with a confident commit message.
- **Hold the code still.** No edits until the cause is known; no destructive
  recovery, ever.
