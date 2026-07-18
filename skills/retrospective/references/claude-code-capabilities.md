# Claude Code capability map: where a fix lands

Each proposed improvement should target a real Claude Code mechanism. Match the root cause (from the taxonomy) to the right surface below. This is the "modern tools" the retrospective routes fixes into.

## Durable instructions & knowledge

- **CLAUDE.md** (`~/.claude/CLAUDE.md` global, or project `./CLAUDE.md`) — always-loaded rules and conventions. For preferences and policies that should hold every session. Keep it a tight map, not an encyclopedia; link out to deeper docs.
- **rules/*.md** — focused standards (e.g. `rules/code-style.md`, `rules/testing.md`) referenced from CLAUDE.md. Put coding/testing conventions here, not inline.
- **Memory** (`~/.claude/projects/<slug>/memory/` + `MEMORY.md` index) — one fact per file with frontmatter (`type: user | feedback | project | reference`). Use for durable facts about the user, confirmed feedback on how to work, ongoing project context, and external pointers. Add a one-line pointer to `MEMORY.md`. Prefer this for things learned *this session* that should persist. Check for an existing file before adding a duplicate.

## Reusable procedures & delegation

- **Skills** (`~/.claude/skills/<name>/SKILL.md`, or project `.claude/skills/`) — package a recurring multi-step procedure with progressive disclosure (a tight SKILL.md + reference files loaded on demand). If a relevant skill *existed but didn't fire*, the fix is usually a sharper `description`/trigger phrasing, not new content. If a procedure was reinvented from scratch, the fix is a new skill.
- **Subagents** (`.claude/agents/` or the Agent tool's types) — delegate bounded, context-heavy work (broad search, independent review) so the main thread stays focused. Fix "main context got flooded by a wide search" by delegating to `Explore`/`general-purpose`; fix "trivial task fanned out to many agents" by doing it inline.
- **Slash commands** — user-invoked entry points. A frequently repeated manual sequence may deserve one.

## Mechanical enforcement (settings.json)

Use the **`update-config` skill** to edit settings safely. The harness — not the model — enforces these, so they cannot be forgotten:

- **Hooks** — run a command on an event (e.g. auto-format on `PostToolUse` after Edit/Write, block a footgun on `PreToolUse`, run tests on `Stop`). The right home for "the agent keeps forgetting to do X every time."
- **Permissions** — allow/deny/ask rules. Tighten to gate risky actions (deny destructive commands); loosen with an allowlist of safe read-only commands to cut permission-prompt friction (see the `fewer-permission-prompts` skill).
- **Permission modes** — plan mode (read-only until a plan is approved), accept-edits, etc.
- **Env vars** — model, behavior toggles.

## Capabilities & integrations

- **MCP servers / tools** — add a missing capability (a connector, an API, a data source) so the agent can act instead of working around the gap.
- **Tool search / progressive tool loading** — surface specialized tools on demand rather than all up front.

## Verification & regression guards

- **Tests / evals** — convert "this bug shipped" into a regression test or eval fixture. The `code-review` / `verify` skills and CI gates are where "claimed done without proof" gets enforced.

## In-session habits (workflow notes)

When the fix is a better habit rather than a new artifact, name the native feature the agent should have used:

- **Plan mode / clarifying first** on ambiguous or multi-step asks (prevents building the wrong thing → the top cause of correction rounds).
- **TodoWrite** to track long multi-step work so steps aren't dropped.
- **Parallel tool calls** — batch independent reads/searches in one message.
- **Cache-aware context** — keep volatile content low in context to protect the prompt-cache prefix; avoid needless re-reads.
- **`/code-review`, `verify`, `rails-ui-review`** before declaring a change done.

## Routing cheatsheet

| Root cause | First-choice surface |
|---|---|
| Unstated user preference | memory (`user`/`feedback`) |
| Project-wide convention | CLAUDE.md / rules |
| Guessed instead of read | source-of-truth pointer + instruction |
| Forgot to do X every time | hook (settings.json) |
| Took risky action unprompted | permission rule / approval policy |
| Prompt-spam on safe commands | permission allowlist |
| Reinvented a procedure | new skill |
| Right skill didn't fire | sharpen skill description/triggers |
| Wide search flooded context | delegate to a subagent |
| Bug shipped unguarded | test / eval fixture |
| Built wrong thing | plan-mode / clarify-first instruction |
