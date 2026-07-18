---
name: rails-api
description: Ruby on Rails patterns when building JSON APIs
---

When writing JSON API endpoints:
- Always use the jbuilder gem to build a JSON response.
- Return consistent error formats with a clear message and an error code that clients can reliably check against.
- Consider backwards compatibility when changing API responses. Add new fields without removing old ones, and version the API if you need to make breaking changes - ask.
