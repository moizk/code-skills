#!/usr/bin/env bash
# Installs this repo's skills, agents, and rules into Cursor.
#
#   skills/*  -> ~/.cursor/skills/<name>   (symlink; edits apply immediately)
#   agents/*  -> ~/.cursor/agents/<name>   (symlink; edits apply immediately)
#   rules/*   -> ~/.cursor/rules/<name>.mdc (converted copy; re-run after editing)
#
# Rules need conversion because Cursor requires .mdc files with
# description/globs/alwaysApply frontmatter, while this repo keeps them as
# plain .md with an optional `paths:` list. A rule with `paths:` becomes a
# glob-scoped rule; a rule without frontmatter becomes alwaysApply: true.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$HOME/.cursor/skills"
AGENTS_DIR="$HOME/.cursor/agents"
RULES_DIR="$HOME/.cursor/rules"
MARKER="synced-from"

mkdir -p "$SKILLS_DIR" "$AGENTS_DIR" "$RULES_DIR"

echo "== Skills =="
for skill in "$REPO_DIR"/skills/*/; do
  name=$(basename "$skill")
  if [ ! -f "$skill/SKILL.md" ]; then
    echo "  skip $name (no SKILL.md)"
    continue
  fi
  ln -sfn "${skill%/}" "$SKILLS_DIR/$name"
  echo "  link $name"
done

echo "== Agents =="
for agent in "$REPO_DIR"/agents/*.md; do
  name=$(basename "$agent")
  ln -sfn "$agent" "$AGENTS_DIR/$name"
  echo "  link $name"
done

# Remove broken symlinks (e.g. a skill/agent deleted or renamed in the repo).
find "$SKILLS_DIR" "$AGENTS_DIR" -maxdepth 1 -type l ! -exec test -e {} \; -print -delete |
  while read -r stale; do echo "  prune $(basename "$stale")"; done

echo "== Rules =="
frontmatter_of() {
  awk 'NR==1 && /^---$/ { in_fm = 1; next } in_fm && /^---$/ { exit } in_fm' "$1"
}

body_of() {
  if [ "$(head -n1 "$1")" = "---" ]; then
    awk 'fences < 2 && /^---$/ { fences++; next } fences == 2' "$1"
  else
    cat "$1"
  fi
}

for rule in "$REPO_DIR"/rules/*.md; do
  name=$(basename "$rule" .md)
  dest="$RULES_DIR/$name.mdc"

  body=$(body_of "$rule")
  globs=$(frontmatter_of "$rule" |
    sed -n 's/^[[:space:]]*-[[:space:]]*"\{0,1\}\([^"]*\)"\{0,1\}[[:space:]]*$/\1/p' |
    paste -s -d, -)
  description=$(printf '%s\n' "$body" | sed -n 's/^# \(.*\)/\1/p' | head -n1)

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
  echo "  write $name.mdc${globs:+ (globs: $globs)}"
done

# Prune generated rules whose source file no longer exists. Only touches
# files carrying our marker, so hand-made global rules are left alone.
for installed in "$RULES_DIR"/*.mdc; do
  [ -e "$installed" ] || continue
  source_path=$(sed -n "s/^# ${MARKER}: //p" "$installed" | head -n1)
  if [ -n "$source_path" ] && [ ! -e "$source_path" ]; then
    rm "$installed"
    echo "  prune $(basename "$installed")"
  fi
done

echo "Done. Reload the Cursor window to pick up changes."
