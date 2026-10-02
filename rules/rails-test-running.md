---
paths:
  - "**/spec/**/*.rb"
  - "**/test/**/*.rb"
---

# Rails — running the test suite: one command, parallel by default, nothing hidden

A green run must be truly green and a red run must mean broken code, not a broken
harness. These rules apply whenever you run or interpret a Rails test run.

## One command
- **Run the suite the way the repo runs it:** `bundle exec rspec`. If the project has a parallel-by-default wrapper (`.rspec` requiring a `parallel_by_default` file, a `bin/pspec`), every rspec invocation already goes through it. Don't call `parallel_rspec` directly or invent flags.
- **Line numbers don't survive a parallel run.** `spec/foo_spec.rb:42` is widened to the whole file and the wrapper warns. To run one example, use the single-process escape hatch (`PSPEC=0 bundle exec rspec spec/foo_spec.rb:42`) or `-e 'example name'`.
- **Debugging needs the single-process path.** `binding.irb` and `debug` only work under `PSPEC=0`.
- **Don't raise the worker count to go faster.** It is measured per machine and recorded in a comment; more workers turn passing browser specs flaky. Override `PSPEC_PROCS` only to go lower on a constrained box.

## Pre-run checks are not optional
- **Never set `SKIP_ASSET_CHECK=1` or `SKIP_TESTS=1` to get a faster or greener run.** They exist for emergencies and print a warning for a reason.
- **A failed asset build stops the run. Fix the build**, never test against the old bundle.
- **If the run stops because `schema.rb` is behind `db/migrate`, run `db:migrate`.** Never `db:reset` or drop the test databases to move past it (see the migrations rule).
- **"Waiting for a database slot" means another run is active in this checkout.** Wait for it; don't kill the other process or delete `tmp/pspec_slots/`.

## Read the whole summary
- **A "Passed on retry" section is a list of bugs, not passes.** Report every entry as a flaky test to fix, with its attempt count. Never describe such a run as fully green.
- **Check the ledger for repeat offenders** before fixing a flake in isolation:

```
cut -f2 tmp/flaky_examples.log | sort | uniq -c | sort -rn
```

- **A storm of Capybara timeouts across many system specs is an environment problem**, not dozens of independent bugs. Suspect stale assets, a stale schema, or a leaked shared service; rebuild and rerun before touching a single spec.
- **Widened filters, skipped checks, and retries always print a warning.** If you see one in the output, say so in your report.

## When the project has none of this
- Still never share mutable state between runs or workers, still run the full file rather than silently more than asked, and still report retries. The isolation and harness rules describe how to add the pieces.
