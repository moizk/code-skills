---
paths:
  - "**/*.rb"
---

# Rails — code style

Applies to any Ruby on Rails project.

## Class definitions
- **Define namespaced classes inline** with the compact form: `class Module1::Class1`, not nested `module Module1; class Class1; end; end`.

## ActiveRecord callbacks
- **Keep business logic out of `before_*` / `after_*` callbacks.** Put it in the service or the controller flow that drives the change, where it's explicit and testable in isolation.
- **Callbacks hide side effects** — they fire on every save from any code path (console, imports, tests, nested updates), making behavior hard to predict and tests brittle.
- **Reserve callbacks for genuinely intrinsic, record-local concerns** — normalizing an attribute before validation, maintaining a derived column, writing an audit/log entry, cleaning up owned resources. If the logic spans models, calls external systems, or orchestrates a workflow, it belongs in a service.

## Controllers — auth first
- **Every controller action enforces authentication and authorization.** A reader should see both before any work happens.
- Authenticate the request (e.g. Devise `authenticate_user!`, applicant OTP session) — never assume a logged-in user.
- Authorize the specific action against the specific resource with the project's policy layer before acting on it. Don't rely on hidden UI or unguarded scopes as the only gate.

## Migrations
- **Name migration files with a real, current timestamp** (`YYYYMMDDHHMMSS`, the actual UTC date/time you create it) — generate it from the clock (`rails g migration`, or `date -u +%Y%m%d%H%M%S`), never hand-write or copy one. Stale or invented prefixes collide with existing migrations and produce duplicate-timestamp errors, and a prefix earlier than an already-run migration silently won't run.
- **Every migration must be reversible** — `db:rollback` then `db:migrate` again must both succeed with no error. If Rails can't infer the inverse (e.g. `change_column`, raw `execute`, data backfills, dropping a column with options), don't rely on `change`; write explicit `up`/`down` methods (or `reversible do |dir|`) so `down` cleanly restores the prior schema. Verify by actually rolling back and re-migrating before finishing.
- **Never edit a migration that has already run** — anything already recorded in `schema_migrations`, *including unshipped local ones you migrated this session*. Editing it in place forces a `db:reset` / full drop to reconcile, which destroys local data and diverges every other environment.
- **Never drop or reset the entire database** to make a schema change take effect. That is not an acceptable way to apply a migration change.
- To change or undo an already-run migration, do one of two things: **(a) roll it back** (`db:rollback` / the migration's `down`), correct it, and re-migrate; or **(b) add a new migration** carrying the corrective expression (`remove_column`, `change_column`, `rename_column`, …) so existing databases move forward cleanly with `db:migrate`.
- **Always ask the user which option** (rollback vs. new migration) before proceeding — do not pick on their behalf.

## Enums
- Use Rails' built-in `enum` with string values. Do not use DB-level enums - they are inflexible and not worth the complexity. Use DB string columns for enums. Use the `suffix: true` option to avoid method name conflicts and improve readability. Do not add DB-backed default string values for the enums as well.

Example:
```ruby
  enum :status, {
    pending: 'pending',
    completed: 'completed',
    declined: 'declined',
  }, default: :pending, suffix: true
```

## Service objects
- **Put complex business logic in service objects**, not in controllers or fat models.
- **A service has exactly one public method: `call`.** All other methods are private. If you need to expose the service as a one-liner, a class-level `self.call(...)` that instantiates and delegates to the instance `#call` is fine.
- **Multiple public methods means it's not really a service.** Either it's a different kind of object (a query, a builder, a presenter, a plain model), or it's doing several jobs and should be **split into multiple single-purpose services**.
- Name services after the action they perform (a verb phrase) and **suffix the class name with `Service`**, e.g. `CreateLeaseOfferService`, `SyncNooklynLeasesService`.
- Services do not throw exception. Instead, they return a result object indicating success or failure, and the caller handles the flow accordingly.
- **Use instance variables (`@`) for the params you receive** — don't add redundant `attr_reader`s for them.

### Common result object
- **Every service returns a shared Result object** carrying a success/failure status and a payload — never raw booleans, nils, or domain objects returned ad hoc.
- Callers branch on the status (`result.success?` / `result.failure?`) and read data from the payload. Reuse the project's existing Result type if one exists; introduce a single shared one if it doesn't, rather than per-service result shapes.

## Keep controllers thin
- Controllers parse params, invoke a service, and render/redirect based on the result. **No business logic in controllers.**
- A controller action should read as: authorize → call service → handle `success`/`failure` → respond.

## Models vs services
- **Model-related behavior stays in the model** — associations, scopes, validations, simple derived attributes, and logic that's intrinsic to that single record. Don't extract these into services.
- Reach for a service when logic **spans multiple models, calls external systems, or orchestrates a multi-step workflow** — anything beyond a single record's own concerns.
