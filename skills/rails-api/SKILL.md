---
name: rails-api
description: "Use when building or changing JSON API endpoints in a Rails app — 'add an API endpoint', 'return JSON from this action', 'build the API for X', 'change this API response'. Covers response building with the project's existing JSON builder, consistent error formats with stable error codes, authentication and authorization on every endpoint, pagination, and backwards-compatible response evolution (add fields, don't remove; version on breaking changes)."
---

# Rails API

When writing JSON API endpoints:

- **Prefer the project's existing JSON builder.** Match how the codebase already
  renders JSON — jbuilder templates, serializer classes, or plain hashes — rather
  than introducing a second style. If the project has no convention yet, pick one
  deliberately and use it consistently.
- **Return consistent error formats** with a clear message and a stable,
  machine-checkable error code, in the same shape on every endpoint — clients
  should be able to handle errors in one place.
- **Use the right status codes.** 200/201/204 for success, 401 vs 403 for
  authentication vs authorization, 404 for missing (or not-yours-to-know), 422
  for validation failures, 429 for rate limits. Never 200 with an error body.
- **Authenticate and authorize every endpoint** — object-level, not just
  logged-in: an ID in the URL is untrusted input. Scope every query to the
  current actor/tenant.
- **Paginate every collection endpoint** from the start, following the project's
  existing pagination style — an unbounded index is a production incident waiting
  for data.
- **Consider backwards compatibility when changing responses.** Add new fields
  without removing or renaming old ones; version the API if you need a breaking
  change — and ask before making one.

Related: the endpoint's data flow (controller → service → job) is planned in
`data-flow-plan`; slow or external work belongs in a background job (`async-jobs`).
