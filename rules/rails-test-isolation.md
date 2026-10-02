---
paths:
  - "**/spec/support/**/*.rb"
  - "**/spec/rails_helper.rb"
  - "**/spec/spec_helper.rb"
  - "**/config/database.yml"
  - "**/config/environments/test.rb"
---

# Rails — test isolation: every worker of every run owns its own state

Separate databases are not enough. Any server shared between workers, or between
two runs in one checkout, becomes a channel through which one spec breaks another.

## The one question
- **For every stateful resource the app touches, ask: does every worker of every run get its own?** Database, Redis, ActionCable, ActiveJob, HTTP, Elasticsearch, S3, a scratch directory. If the answer is no, add a per-process stand-in or a per-slot name before writing specs that depend on it.

## Databases
- **Per-worker names come from the environment, read before Rails boots:**

```yaml
test:
  database: <%= ENV.fetch("DATABASE_NAME", "app") %>_test<%= ENV["TEST_ENV_NUMBER"] %>
```

- **System specs clean with DatabaseCleaner's `deletion` strategy, never `truncation`.** Truncation locks every table in one statement; eight workers doing that at once overran Postgres' lock table (`out of shared memory`). Deletion was also about five times faster.
- **If cleanup fails, run `clean_with` again before the next example** so the real error isn't buried under a uniqueness violation.
- **Keep `maintain_test_schema!` but don't rely on it for parallel copies.** It updates only the first database; the wrapper's schema stamp handles the rest.

## Shared services become in-process
- **Redis: every `Redis.new` returns one in-memory fake per process** (`spec/support/fake_redis.rb`, via `Redis.singleton_class.prepend`). Guard it with a mutex, because Capybara's server runs in another thread of the same process.
- **The fake implements only the commands the app uses.** Anything else raises `NoMethodError` on purpose, which is louder than quietly reaching a real server. Add a command when the app starts using it.
- **Don't fake behavior you don't simulate.** If TTLs are ignored, a spec that depends on expiry must fail loudly, not pass on a lie.
- **ActionCable on the `:test` adapter, ActiveJob on `:test` or `:inline`, WebMock blocking all real HTTP.** In Cuprite, block unresolvable hosts (`*.test`, third-party CDNs) so a slow DNS lookup can't fail a visit.
- **A `reset!` in a `before(:each)` may only touch state owned by this process.** If it can reach another worker's data, the resource isn't isolated yet.

## Browser state leaks too
- **Reset the driver's injected scripts after every system spec** in an `after(:each, type: :system)`. Ferrum replays every `evaluate_on_new_document` script into every later page the worker opens, so a fake from one file shows up in the next.
- **Any per-spec stub installed into the browser is torn down in the same spec**, never left for the suite to outlive.

## Retries are recorded, not swallowed
- **System specs may use rspec-retry, but only inside an `around(:each, type: :system)` that records any example which retried and then passed.** One JSON line per record, appended under a `flock` to the file the wrapper names.
- **Never add `retry:` metadata to a unit or request spec.** Those don't talk to a browser; a retry there hides a real bug.
