---
paths:
  - "**/app/jobs/**/*.rb"
  - "**/app/mailers/**/*.rb"
  - "**/app/sidekiq/**/*.rb"
  - "**/app/workers/**/*.rb"
---

# Rails — jobs and mailers: thin triggers that delegate to services

Full guidance for background work lives in the `async-jobs` skill. These are the
rules that always apply when touching one of these files.

## Jobs
- **The job is a trigger, not a home for logic.** `perform` loads the record by ID, calls one service, and returns. The service stays testable and reusable outside the queue.
- **Pass IDs, never objects**, and handle the record being gone by the time the job runs (`find_by` with an early return, or `discard_on ActiveRecord::RecordNotFound`).
- **Enqueue after commit**, from the service below its `transaction` block or from `after_commit`, never inside a transaction.
- **Assume it runs twice and concurrently.** Guard on state or a unique key so a retry can't double-charge or double-send.
- **Choose the queue and retry policy on purpose.** `queue_as` matches urgency; `retry_on` lists transient errors and `discard_on` permanent ones. Never retry validation failures.
- **Name it after what it does, with the `Job` suffix:** `Billing::SendInvoiceReminderJob`.

## Mailers
- **One mailer per domain, one method per email, `Mailer` suffix.** Methods receive their inputs through `.with(...)` params, not positional arguments.
- **Mailers format and render; they don't decide.** Whether to send and to whom is the calling service's job. A mailer never queries for recipients or checks preferences.
- **Always `deliver_later` from application code.** `deliver_now` is for the console and tests.
- **Templates format through presenters or helpers** and use the same locale files as the rest of the app.
