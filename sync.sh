#!/usr/bin/env bash
# Installs this repo's skills, agents, and rules into Cursor AND Claude Code.
#
#   skills/*  -> ~/.cursor/skills/<name>  + ~/.claude/skills/<name>  (symlink; edits apply immediately)
#   agents/*  -> ~/.cursor/agents/<name>  + ~/.claude/agents/<name>  (symlink; edits apply immediately)
#   rules/*   -> ~/.cursor/rules/<name>.mdc                          (converted copy; re-run after editing)
#   CLAUDE.md -> ~/.claude/CLAUDE.md                                 (marker-guarded copy; re-run after editing)
#
# Rules need conversion because Cursor requires .mdc files with
# description/globs/alwaysApply frontmatter, while this repo keeps them as
# plain .md with an optional `paths:` list. A rule with `paths:` becomes a
# glob-scoped rule; a rule without frontmatter becomes alwaysApply: true.
# Claude Code has no rules mechanism; its global preferences come from the
# synced ~/.claude/CLAUDE.md instead.
#
# Usage: ./sync.sh [--dry-run|--check]
#   --dry-run  print what would happen without writing anything
#   --check    run validate.sh (frontmatter/description/symlink checks) and exit

set -euo pipefail
shopt -s nullglob

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

[ "${1:-}" = "--check" ] && exec "$REPO_DIR/validate.sh"

DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1 && echo "(dry-run: nothing will be written)"
CURSOR_SKILLS="$HOME/.cursor/skills"
CURSOR_AGENTS="$HOME/.cursor/agents"
CURSOR_RULES="$HOME/.cursor/rules"
CLAUDE_SKILLS="$HOME/.claude/skills"
CLAUDE_AGENTS="$HOME/.claude/agents"
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
MARKER="synced-from"

if [ "$DRY_RUN" = 0 ]; then
  mkdir -p "$CURSOR_SKILLS" "$CURSOR_AGENTS" "$CURSOR_RULES" "$CLAUDE_SKILLS" "$CLAUDE_AGENTS"
fi

link() {
  if [ "$DRY_RUN" = 1 ]; then return; fi
  ln -sfn "$1" "$2"
}

echo "== Skills =="
for skill in "$REPO_DIR"/skills/*/; do
  name=$(basename "$skill")
  if [ ! -f "$skill/SKILL.md" ]; then
    echo "  skip $name (no SKILL.md)"
    continue
  fi
  link "${skill%/}" "$CURSOR_SKILLS/$name"
  link "${skill%/}" "$CLAUDE_SKILLS/$name"
  echo "  link $name (cursor + claude)"
done

echo "== Agents =="
for agent in "$REPO_DIR"/agents/*.md; do
  name=$(basename "$agent")
  link "$agent" "$CURSOR_AGENTS/$name"
  link "$agent" "$CLAUDE_AGENTS/$name"
  echo "  link $name (cursor + claude)"
done

# Remove broken symlinks (e.g. a skill/agent deleted or renamed in the repo).
echo "== Prune broken links =="
for dir in "$CURSOR_SKILLS" "$CURSOR_AGENTS" "$CLAUDE_SKILLS" "$CLAUDE_AGENTS"; do
  [ -d "$dir" ] || continue
  find "$dir" -maxdepth 1 -type l ! -exec test -e {} \; -print | while read -r stale; do
    echo "  prune $stale"
    [ "$DRY_RUN" = 1 ] || rm "$stale"
  done
done

echo "== Rules (cursor) =="
frontmatter_of() {
  awk 'NR==1 && /^---$/ { in_fm = 1; next } in_fm && /^---$/ { exit } in_fm' "$1"
}

# Frontmatter only counts when line 1 is `---` AND a closing `---` exists;
# otherwise a file that merely starts with a horizontal rule would lose its body.
has_frontmatter() {
  [ "$(head -n1 "$1")" = "---" ] &&
    awk 'NR > 1 && /^---$/ { found = 1; exit } END { exit !found }' "$1"
}

body_of() {
  if has_frontmatter "$1"; then
    awk 'fences < 2 && /^---$/ { fences++; next } fences == 2' "$1"
  else
    cat "$1"
  fi
}

for rule in "$REPO_DIR"/rules/*.md; do
  name=$(basename "$rule" .md)
  dest="$CURSOR_RULES/$name.mdc"

  body=$(body_of "$rule")
  globs=$(frontmatter_of "$rule" |
    sed -n 's/^[[:space:]]*-[[:space:]]*"\{0,1\}\([^"]*\)"\{0,1\}[[:space:]]*$/\1/p' |
    paste -s -d, -)
  description=$(printf '%s\n' "$body" | sed -n 's/^# \(.*\)/\1/p' | head -n1)

  if [ "$DRY_RUN" = 0 ]; then
    {
      echo "---"
      echo "# ${MARKER}: ${rule}"
      echo "description: \"${description:-$name}\""
      if [ -n "$globs" ]; then
        echo "globs: ${globs}"
        echo "alwaysApply: false"
      else
        echo "alwaysApply: true"
      fi
      echo "---"
      echo
      printf '%s\n' "$body"
    } > "$dest"
  fi
  echo "  write $name.mdc${globs:+ (globs: $globs)}"
done

# Prune generated rules whose source file no longer exists. Only touches
# files carrying our marker, so hand-made global rules are left alone.
for installed in "$CURSOR_RULES"/*.mdc; do
  [ -e "$installed" ] || continue
  source_path=$(sed -n "s/^# ${MARKER}: //p" "$installed" | head -n1)
  if [ -n "$source_path" ] && [ ! -e "$source_path" ]; then
    echo "  prune $(basename "$installed")"
    [ "$DRY_RUN" = 1 ] || rm "$installed"
  fi
done

echo "== Claude global preferences =="
if [ -e "$CLAUDE_MD" ] && ! grep -q "${MARKER}: ${REPO_DIR}/CLAUDE.md" "$CLAUDE_MD"; then
  echo "  skip ~/.claude/CLAUDE.md (exists and wasn't written by sync — merge manually)"
else
  if [ "$DRY_RUN" = 0 ]; then
    {
      echo "<!-- ${MARKER}: ${REPO_DIR}/CLAUDE.md — edit the repo copy and re-run sync.sh -->"
      cat "$REPO_DIR/CLAUDE.md"
    } > "$CLAUDE_MD"
  fi
  echo "  write ~/.claude/CLAUDE.md"
fi

echo "Done. Reload the Cursor window to pick up changes."
