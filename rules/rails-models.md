---
paths:
  - "**/app/models/**/*.rb"
---

# Rails — models: associations, validations, callbacks, enums, concerns

A model owns one table's data and the rules intrinsic to one record. Anything that
spans models, calls external systems, or orchestrates steps belongs in a service
(see the services rule).

## Associations declare their intent
- **Every `has_many` and `has_one` states `dependent:`** (`:destroy`, `:nullify`, `:restrict_with_error`). Leaving it off is not neutral; it means orphan rows.
- **Every `belongs_to` has a foreign key constraint in the database**, and is `optional: true` only when the column is genuinely nullable.
- **Add `inverse_of`** when Rails can't infer it (custom `foreign_key`, `class_name`, or a scoped association) so in-memory objects stay consistent.

## Validations mirror database constraints
- **Validations are for messages; constraints are for truth.** Every `presence` has `null: false`, every `uniqueness` has a unique index, every `belongs_to` a foreign key. Validations race under concurrency; constraints don't.
- **Keep validations declarative.** A `validate :custom_check` is fine for one record's own invariant. If it needs another table or request state, it belongs in a Form or a Service.

## Scopes
- **Scopes are single-model, composable building blocks:** `active`, `created_since(time)`. No ordering unless the name says so (`newest_first`), no `includes`, no joins into other domains.
- **Never `default_scope`.** It hides rows from every query path, including the console and admin tools.
- **Anything with joins, several filters, or reporting is a Query object**, not a class method on the model.

## Callbacks
- **Keep business logic out of `before_*` and `after_*` callbacks.** They fire on every save from every code path (console, imports, tests, nested saves), so the behavior is invisible at the call site and hard to test in isolation.
- **Reserve callbacks for record-local concerns:** normalizing an attribute before validation, maintaining a derived column, cleaning up owned resources.
- **If a callback must have a side effect, use `after_commit`**, never `after_save` or `after_create`. An email sent from `after_save` survives the rollback that deleted its record.

## Enums
- **Use Rails `enum` backed by a string column.** No database-level enum types and no database default for the column; the default lives in the `enum` declaration.
- **Always pass `suffix: true`** (or `prefix:`) so `status_pending?` can't collide with another enum's `pending?`.

```ruby
enum :status, {
  pending: 'pending',
  completed: 'completed',
  declined: 'declined',
}, default: :pending, suffix: true
```

## Concerns
- **A concern needs two or more includers and a capability name** (`Archivable`, `Searchable`). A concern with one includer is a fat model split across two files.
- **A concern's contract with its includer is explicit:** the columns it expects and the methods the includer must define. If it needs to know which class included it, it isn't shared behavior.

## Keep the model about the record
- **Stays in the model:** associations, scopes, validations, enums, simple derived attributes (`full_name`), state predicates (`overdue?`).
- **Leaves the model:** anything touching another aggregate, an external API, mail, jobs, or a multi-step workflow. Put it in a service and call the service from the controller or job.
- **No presentation here.** Formatting dates, currency, or labels belongs in a presenter or helper.
