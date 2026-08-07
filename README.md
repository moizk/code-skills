# code-skills

The foundation of my agentic coding setup: skills, agents, and rules shared
between **Cursor** and **Claude Code**, kept in one repo so both platforms stay
in sync.

## Layout

| Path | What it is |
|---|---|
| `skills/<name>/SKILL.md` | Task playbooks (reviews, planning, Rails patterns, orchestration). Big skills keep detail in `references/` next to the SKILL.md. |
| `skills/_shared/` | Reference docs shared by several skills (not a skill itself; never installed on its own). |
| `agents/<name>.md` | Subagent role definitions (architector, designer, developer, product-manager, reviewer, teamlead). |
| `rules/<name>.md` | Code guidelines. No frontmatter = always applied; a `paths:` list scopes the rule to matching files. |
| `CLAUDE.md` | Global preferences, synced to `~/.claude/CLAUDE.md`. |
| `sync.sh` | Installs everything into both platforms. |
| `validate.sh` | Checks frontmatter, descriptions, and symlinks. |

## Install / update

```sh
./sync.sh            # install into ~/.cursor and ~/.claude
./sync.sh --dry-run  # show what would happen
./sync.sh --check    # run validate.sh only
```

What sync does:

- **Skills and agents are symlinked** into `~/.cursor/{skills,agents}` and
  `~/.claude/{skills,agents}` — edits in the repo apply immediately, no re-sync
  needed.
- **Rules are converted copies** — Cursor needs `.mdc` files with
  `description`/`globs`/`alwaysApply` frontmatter, so `sync.sh` generates them
  into `~/.cursor/rules/`. **Re-run `./sync.sh` after editing a rule.**
- **CLAUDE.md is a marker-guarded copy** to `~/.claude/CLAUDE.md` — re-run after
  editing. If a hand-written file already exists there, sync leaves it alone and
  tells you to merge manually.
- Sync prunes symlinks and generated rules whose source was deleted or renamed.

After syncing, reload the Cursor window (and restart Claude Code sessions) to
pick up changes.

## Writing descriptions (the routing contract)

The `description:` field is the *only* thing the harness reads when deciding
whether a skill/agent fires — the body loads after routing. Broken or truncated
descriptions mean the skill silently never triggers. Rules:

1. **Single-line, double-quoted string.** Never a `>-`/`|` block scalar (Cursor
   shows a literal `>-` as the description) and never an unquoted value
   containing `: ` (breaks YAML parsing entirely — the skill loads with no
   description at all).
2. **Triggers first.** Lead with "Use when…" plus the literal phrases that
   should route here; put "Not for… (use X)" at the end. Harnesses truncate from
   the end, so anything load-bearing goes up front.
3. **Target ~500 chars, hard cap 1024.** `validate.sh` enforces the cap.
4. **Platform-neutral vocabulary.** No Claude-only tool names
   (`AskUserQuestion`, `Task`, `Explore`) — say "ask the user", "delegate a
   broad search", etc., so the text is true in both harnesses.
5. **Skill `name` matches its directory**, agent `name` matches its filename.

Run `./validate.sh` (or `./sync.sh --check`) after editing — it catches all of
the above plus broken symlinks.
