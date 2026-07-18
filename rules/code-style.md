# Code style

Applies to all code, every language.

## Methods
- **Each method does one job.** Prefer short, focused methods with a name that says what they do.
- **But don't over-split.** Extract a method when it earns its name — a reused step, a named concept, or a chunk that hides distracting detail behind intent. A few sequential lines that only run in one place and read fine inline don't need their own method.
- Rule of thumb: extract for clarity or reuse, not to hit a line count. If naming the extracted piece is awkward, it probably shouldn't be extracted.

## Naming
- **Names reveal intent.** A reader should understand what something is from its name alone, without chasing the definition.
- **No abbreviations or single letters** — except conventional loop indices and math (`i`, `x`, `y`). Spell it out: `index`, `request`, `customer`.
- **Booleans read as predicates** — `active?`, `has_offers`, `is_visible`, `valid`. The name should answer a yes/no question.

## Comments
- **Explain why, not what.** The code already says what it does; a comment earns its place by capturing intent, a non-obvious constraint, or the reason behind a surprising choice.
- **No comments that restate the line.** If a comment just narrates the next statement, delete it and let the code speak — or rename things so it reads clearly.
- Prefer a well-named method or variable over a comment whenever you can.
- *THE BEST COMMENT IS A TEST* — The test serves as both documentation and a safety net for future changes.

## Nesting
- **Guard clauses over nested conditionals.** Handle edge cases and bail early (`return`, `next`, `raise`) so the happy path stays at the lowest indentation.
- **Keep nesting shallow.** Deep `if`/`else` pyramids are a signal to invert a condition, extract a method, or return early.
