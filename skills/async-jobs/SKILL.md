---
name: async-jobs
description: Patterns for writing asynchronous background jobs
---

When writing asynchronous background jobs:

- **Keep the job thin.** The job should not hold complex logic — it's a trigger. Extract the real work into a service object (or domain method) and have the job call it. This keeps the logic testable in isolation and reusable outside the job.
- **Design for idempotency and concurrency.** A job can be retried or run more than once, and several instances may run at the same time. Make repeated runs safe (guard on state, use unique keys, upserts, or locks) so a re-run doesn't double-charge, double-send, or corrupt data. Account for concurrent execution where it matters.
- **Decide the retry policy deliberately.** Think about what should happen on failure: how many retries, backoff, and which errors are worth retrying versus failing fast (e.g. don't retry on permanent validation errors). Make sure retries are safe given the idempotency guarantees above.
