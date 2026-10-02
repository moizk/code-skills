---
paths:
  - "**/db/migrate/**/*.rb"
  - "**/db/schema.rb"
  - "**/db/structure.sql"
---

# Rails — migrations: real timestamps, reversible, never edit one that has run

## Creating a migration
1. **Generate it** (`rails g migration ...`) so the timestamp is the real current UTC time. Never hand-write or copy a `YYYYMMDDHHMMSS` prefix: an invented one collides with existing migrations, and one earlier than an already-run migration silently never runs.
2. **Schema, not data.** A migration changes structure. Data backfills get their own migration (or a rake task for large tables) with explicit `up` / `down`, and never load application models. If you must query, define a bare `class Invoice < ApplicationRecord; end` inside the migration.
3. **Make it reversible.** `db:rollback` then `db:migrate` must both succeed. When Rails can't infer the inverse (`change_column`, `execute`, removing a column with options, backfills), write `up` / `down` or `reversible do |dir|`. Verify by actually rolling back and re-migrating before finishing.
4. **Add the constraints with the column.** `null: false` for every required attribute, `foreign_key: true` on every reference, a unique index for every uniqueness validation, an index on every column that will be filtered or joined on.
5. **Enums are string columns** with no database default and no database enum type; the default lives in the model.

## Changing a migration that has already run
- **Never edit it in place**, including unshipped local migrations you ran this session. Anything recorded in `schema_migrations` is history; editing it forces a `db:reset` on every environment.
- **Never drop or reset the database** to make a schema change take effect.
- Choose one of two paths, and **ask the user which one** before proceeding:
  - **(a) Roll it back** (`db:rollback`), fix it, re-migrate. Fine while it exists only on your machine.
  - **(b) Add a corrective migration** (`remove_column`, `change_column`, `rename_column`). Required once any other person or environment has run it.

## Safety on large tables
- **Add indexes with `algorithm: :concurrently`** and `disable_ddl_transaction!` so the table isn't locked.
- **Adding `NOT NULL` or a default to an existing big table is two steps:** add the column nullable, backfill in batches, then add the constraint.
- **Removing or renaming a column that running code still reads is a deploy outage.** Add it to `ignored_columns` first, ship, then remove the column in the next release.
- If the project uses `strong_migrations`, follow its prompts rather than disabling the check.

## schema.rb / structure.sql
- **Never hand-edit.** It is generated output; fix the migration and regenerate.
- **Commit it alongside the migration** so the diff shows exactly what changed.
