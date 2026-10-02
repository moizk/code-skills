---
paths:
  - "**/bin/pspec"
  - "**/spec/pspec_*.rb"
  - "**/spec/parallel_by_default.rb"
  - "**/.rspec"
---

# Rails — test harness code: kernel locks, loud warnings, fail-stop pre-checks

The harness is code that can silently lie about the suite. Hold it to a higher
standard than the specs it runs.

## Taking over rspec
- **The parallel wrapper takes over only when all of these hold:** `TEST_ENV_NUMBER` is unset (so workers never re-enter), its own marker (`PSPEC_ACTIVE`) is unset (fork-bomb guard), `PSPEC` is not `0`, and the running program is `rspec`, not a Rake task or console that loaded the file.
- **Rewrite arguments for parallel_tests explicitly.** Anything that isn't an existing path (`--tag`, `-e`) goes through `-o`. Strip `:line` suffixes, run the whole file, and **print a warning**. Never run more than asked silently.
- **Restore `--format progress`** when the caller passed no format; any `--format` of your own silences rspec's default output.

## Locks belong to the kernel
- **Coordinate with `flock`, never marker files or PID files.** A process that dies releases its lock; there is no cleanup step to forget.
- **Slot locks are exclusive and non-blocking** on `tmp/pspec_slots/<n>.lock`. When every slot up to `PSPEC_MAX_SLOTS` is taken, say so and wait.
- **Open lock handles with `close_on_exec = false`** so child processes inherit them, and **keep a reference to every handle for the life of the process.** A handle closed by garbage collection hands your databases to another run mid-suite.
- **Apply the slot by exporting `DATABASE_NAME` before Rails boots.** Nothing inside the app knows about slots.

## Pre-run checks stop on failure
- **Stale means: an output is missing, or the newest source mtime is later than the oldest output mtime.** No hashing; a false positive costs one rebuild and a false negative needs a back-dated file.
- **A failed build stops the run.** Testing against the old bundle is never the fallback.
- **`touch` outputs after a build**, because bundlers skip writing unchanged files and the bundle would look stale forever.
- **Run the check under a `flock`** so two simultaneous runs don't both build into one directory.
- **Schema stamp per slot = SHA256 of `schema.rb` + list of migration versions + worker count.** Versions catch back-dated migrations; worker count creates databases when `PSPEC_PROCS` rises. Reload only when the stamp changes.
- **Before loading schema, compare `schema.rb` with `db/migrate`.** If migrations are unrun, stop and list them with "run db:migrate". Don't ask the test database whether it is current; that is the thing that can be stale.

## Runtime log
- **Write each run's timings to a scratch file and merge under a `flock`.** The stock RuntimeLogger truncates, so a `spec/models` run would delete every system-spec timing.
- **Keep the previous timing for any file whose example failed or retried.** Timeouts times retries is not the file's real cost.
- **Drop entries whose path no longer exists**, and read and write the log as UTF-8 explicitly. A US-ASCII locale (cron, Capistrano, CI images) plus one non-ASCII example name is a red run.

## Retry report
- **After the parallel run, print a "Passed on retry (N)" section:** location, attempt, description, one-line error, and how often the example already appears in `tmp/flaky_examples.log`. Append each entry to that ledger as tab-separated date, location, attempts, error.
- **The single-process path reports for itself** from an `after(:suite)` `at_exit` hook, since no wrapper sits above it.

## Every escape hatch is loud, every piece is tested
- **Each env override (`PSPEC=0`, `SKIP_ASSET_CHECK`, `PSPEC_PROCS`) prints that it is active.**
- **Worker count is measured, recorded in a comment with the numbers, and overridable.** Half the cores is the starting point, not the answer.
- **Each harness file has its own spec** (`spec/pspec_*_spec.rb`). Add `tmp/pspec_slots/`, the runtime log, and `flaky_examples.log` to `.gitignore`.
