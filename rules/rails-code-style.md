---
paths:
  - "**/*.rb"
---

# Rails — code style: object vocabulary, dependency direction, Ruby conventions

Applies to any Ruby on Rails project. These rules cover every Ruby file; models,
controllers, services, migrations, and jobs each have their own rule that loads
alongside this one when you edit those directories.

## Every piece of logic has one home
Rails codebases scale on a closed vocabulary of object kinds. Pick the kind from
this table before writing code. If nothing fits, the design is off, not the table.

| Kind | Directory | Suffix | Public API | Owns |
|---|---|---|---|---|
| Model | `app/models` | — | associations, scopes, validations | one record's own data and rules |
| Service | `app/services` | `Service` | `call` → Result | writes spanning models, workflows, external calls |
| Query | `app/queries` | `Query` | `call` → Relation | reads spanning joins or taking several filters |
| Policy | `app/policies` | `Policy` | action predicates + `Scope` | authorization, nothing else |
| Form | `app/forms` | `Form` | attributes, `valid?` | validating input that maps to several models |
| Presenter | `app/presenters` | `Presenter` | view-facing methods | display logic kept out of views and models |
| Job | `app/jobs` | `Job` | `perform` | scheduling; delegates to a service |
| Mailer | `app/mailers` | `Mailer` | one method per email | templates; sent with `deliver_later` |

- **Dependencies point one way:** controllers and jobs → services → models, queries, mailers. Models call nothing above them: no services, no controllers, no `current_user`, no request state.
- **Match the project before this table.** If the codebase already has `app/operations` or its own Result type, follow it. The table decides only when the project has no convention yet.
- **A new kind of object needs a row here first** (suffix, directory, public API) before the first instance is written. An unlisted `Manager`, `Handler`, or `Util` is a smell.

## Class definitions
- **Define namespaced classes with the compact form:** `class Billing::ChargeCardService`, not nested `module Billing; class ChargeCardService; end; end`.
- **One class per file, path mirrors namespace:** `Billing::ChargeCardService` lives in `app/services/billing/charge_card_service.rb`. Zeitwerk autoloading depends on it.

## Method signatures
- **Keyword arguments for anything beyond two parameters, and for every boolean.** `create(user:, plan:, trial: false)` reads at the call site; `create(user, plan, false)` does not.
- **Trailing commas in multi-line literals** (arrays, hashes, argument lists) so adding an entry is a one-line diff.
- **Guard clauses over nesting.** Bail early so the happy path sits at the lowest indentation (see the general code-style rule).

## Time and money
- **`Time.current` and `Date.current`, never `Time.now` or `Date.today`.** The latter ignore the app time zone and break under `travel_to` in tests.
- **Money is an integer in minor units (cents) or a `decimal` column, never a `Float`.**
- **Inject clocks and random values** where logic depends on them, so tests can control them.

## Configuration and constants
- **No magic numbers or inline URLs.** Name them as constants on the class that owns them (`MAX_ATTEMPTS = 3`).
- **Environment-dependent values go through one place:** `Rails.application.config_for`, credentials, or a single config object. Never read `ENV[]` from models, services, or controllers.

## Errors
- **Expected failures are return values; unexpected failures raise.** A service returns a failed Result for "card declined". A record that must exist but is missing raises and reaches the error tracker.
- **Never rescue `StandardError` or `Exception` to swallow.** Rescue the narrowest class you can actually handle and re-raise or report everything else.
- **Custom errors inherit from one app base class** (`class AppError < StandardError`) so the base controller can map them with a single `rescue_from`.

## Formatting is RuboCop's job
- The project's `.rubocop.yml` decides indentation, quotes, and line length. Don't restate formatting here; run the linter and fix what it reports.
- Follow the existing files on `# frozen_string_literal: true`.

## Related
- JSON endpoints: `rails-api` skill. Background work: `async-jobs` skill. ERB, helpers, Stimulus: `rails-ui-frontend` rule.
