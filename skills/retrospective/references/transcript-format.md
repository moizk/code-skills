# Transcript format & locating a session

Claude Code writes one JSONL file per session under:

```
~/.claude/projects/<project-slug>/<sessionId>.jsonl
```

`<project-slug>` is the absolute working directory with every `/` and `.` replaced by `-`:

```
/Users/me/app      -> -Users-me-app
/Users/me/.claude  -> -Users-me--claude   (note the double dash from "/.")
```

The extractor derives this from the cwd automatically. The **current** session is the most-recently-modified `*.jsonl` in that folder (it is appended to live). A `memory/` subfolder may sit alongside the transcripts — that is the memory store, not a transcript.

## Record types (top-level `type`)

| type | meaning |
|---|---|
| `user` | a genuine human turn **or** a tool result being fed back to the model |
| `assistant` | a model turn: `thinking` / `text` / `tool_use` blocks + `usage` |
| `attachment` | injected context (file snapshots, added files) |
| `file-history-snapshot` | editor file-state checkpoint |
| `ai-title`, `last-prompt`, `queue-operation` | harness bookkeeping |

## Fields that matter for a retrospective

- `message.content` — string (real user prompt) **or** a list of blocks.
- Block types: `thinking` (raw reasoning — **never surface it**), `text`, `tool_use` (`id`, `name`, `input`), `tool_result` (`tool_use_id`, `is_error`, `content`).
- `message.usage` on assistant records — `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`. The cache-read share is the prompt-cache efficiency signal.
- `attributionSkill` (assistant) — which skill was active for that turn.
- `isSidechain: true` — a subagent / Task turn rather than the main thread.
- `userType: "external"` — a real human prompt (vs. injected/tool content).
- `timestamp`, `uuid`, `sessionId`, `cwd`, `gitBranch`, `version`.

## Distinguishing real user prompts from noise

A `user` record is a **genuine human turn** when `content` is a string, or a block list with a `text` block and **no** `tool_result`. Exclude:

- records whose text starts with `<system-reminder>` or `<command-` (harness/slash-command injection),
- records carrying `tool_result` blocks (those are tool outputs, not the human talking),
- `isSidechain` records (subagent internals).

The extractor already applies these rules; `user_prompts` is the clean, ordered list of what the human actually said.

## Linking a tool error back to its call

`tool_result.tool_use_id` matches the `id` of the `tool_use` block that produced it. The extractor builds this map so each entry in `tool_errors` is labeled with the tool name.

## Inspecting a specific moment

The summary truncates snippets and never includes raw `thinking`. When you need the full text around a flagged event, grep the transcript by `uuid` (the JSONL key is `"uuid":"<id>"`) and read just that record — do not load the whole file into context.
