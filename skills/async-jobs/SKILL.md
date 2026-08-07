---
name: async-jobs
description: "Use when writing or changing asynchronous background jobs — Sidekiq/ActiveJob workers, scheduled tasks, queued or deferred work — 'add a background job', 'move this to a worker', 'process this async', 'run this in the background'. Covers keeping jobs thin (the job triggers, a service does the work), idempotency and safe retries under concurrency, deliberate retry policy, enqueue-after-commit, passing IDs not objects, and testing jobs in isolation."
---

# Async Jobs

When writing asynchronous background jobs:

- **Keep the job thin.** The job is a trigger, not a home for logic: parse args,
  call a service object (or domain method), report. Logic in the service stays
  testable in isolation and reusable outside the job.
- **Pass IDs, not objects.** A serialized object goes stale between enqueue and
  perform (and bloats the queue); re-fetch by ID inside the job and handle the
  record being gone by the time it runs.
- **Enqueue after commit.** A job enqueued inside a transaction can run before its
  row exists — use the framework's after-commit hook (or enqueue outside the
  transaction) so a job never races its own data.
- **Design for idempotency and concurrency.** A job can be retried or run more
  than once, and several instances may run at the same time. Make repeated runs
  safe (guard on state, unique keys, upserts, or locks) so a re-run doesn't
  double-charge, double-send, or corrupt data.
- **Decide the retry policy deliberately.** How many retries, what backoff, and
  which errors are worth retrying versus failing fast (don't retry permanent
  validation errors). Make sure retries are safe given the idempotency guarantees
  above.
- **Mind the queue.** Put the job on a queue whose latency matches its urgency;
  don't let slow bulk work share a queue with user-facing jobs.
- **Test the job in isolation.** Unit-test the service logic directly; test the
  job for its contract — it enqueues with the right args, calls the service, is
  idempotent on re-run (run it twice in the test), and retries/discards the right
  error classes.

Related: whether work runs inline or in a job is an architecture decision — see
`data-flow-plan`. Jobs that call AI/external APIs: see `ai-features`.
