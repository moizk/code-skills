# Testing

- **Every new feature must be covered with tests** unless the request explicitly says otherwise.
- Before finishing, **run the existing tests** and confirm they pass. If any fail, decide whether it's a bug in the new feature or an outdated/stale test.
- If it's a bug, **always fix the code rather than the test.** Only change a test when it's genuinely outdated and the code is correct.
- Every new page should be covered with an end-to-end UI test. If the page is simple and doesn't have complex interactions, a single test that verifies the main user flow may be sufficient. For more complex pages, consider additional tests to cover edge cases and different user interactions.

## Rules
- Test behavior, not implementation details
- Each test should verify one concept
- Tests should be independent — no shared mutable state between tests
- Every test name should read like a specification
- Keep in mind the testing pyramid: prefer unit tests for core logic, and use integration/feature tests for end-to-end flows and UI interactions.
- Keep in mind the possible flakiness of time-sensitive tests. If necessary, use time-mocking libraries to control time in tests.
