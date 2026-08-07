#!/usr/bin/env bash
# Validates the repo so broken routing can't sneak back in:
#   - every SKILL.md / agent frontmatter parses as YAML
#   - description present, single-line, <= 1024 chars
#   - skill/agent `name` matches its directory/filename
#   - agents' `skills:` entries exist in skills/
#   - no broken symlinks anywhere in the repo
#
# Run directly, or via ./sync.sh --check. Exits non-zero on any failure.

set -euo pipefail
cd "$(dirname "$0")"

ruby - <<'RUBY'
require "yaml"

failures = []

def frontmatter(path, failures)
  text = File.read(path)
  unless text.start_with?("---\n")
    failures << "#{path}: missing frontmatter"
    return nil
  end
  raw = text.split(/^---\s*$/, 3)[1]
  begin
    YAML.safe_load(raw)
  rescue Psych::SyntaxError => error
    failures << "#{path}: YAML parse error — #{error.message}"
    nil
  end
end

def check_description(path, fm, failures)
  description = fm["description"]
  if description.nil? || description.strip.empty?
    failures << "#{path}: description missing or empty"
  elsif description.include?("\n")
    failures << "#{path}: description is multi-line — Cursor truncates/mangles block scalars"
  elsif description.length > 1024
    failures << "#{path}: description too long (#{description.length} > 1024 chars)"
  end
end

skill_names = []
Dir.glob("skills/*/SKILL.md").sort.each do |path|
  fm = frontmatter(path, failures) or next
  dir_name = File.basename(File.dirname(path))
  skill_names << dir_name
  failures << "#{path}: name '#{fm["name"]}' != directory '#{dir_name}'" if fm["name"] != dir_name
  check_description(path, fm, failures)
end

# Underscore-prefixed dirs (skills/_shared/) hold shared references, not skills.
Dir.glob("skills/*").sort.each do |dir|
  next unless File.directory?(dir)
  next if File.basename(dir).start_with?("_")
  failures << "#{dir}: no SKILL.md" unless File.file?(File.join(dir, "SKILL.md"))
end

agent_count = 0
Dir.glob("agents/*.md").sort.each do |path|
  agent_count += 1
  fm = frontmatter(path, failures) or next
  file_name = File.basename(path, ".md")
  failures << "#{path}: name '#{fm["name"]}' != filename '#{file_name}'" if fm["name"] != file_name
  check_description(path, fm, failures)
  Array(fm["skills"]).each do |skill|
    failures << "#{path}: references missing skill '#{skill}'" unless skill_names.include?(skill)
  end
end

Dir.glob("rules/*.md").sort.each do |path|
  frontmatter(path, failures) if File.read(path).start_with?("---\n")
end

Dir.glob("**/*", File::FNM_DOTMATCH).each do |entry|
  next unless File.symlink?(entry)
  failures << "#{entry}: broken symlink -> #{File.readlink(entry)}" unless File.exist?(entry)
end

if failures.empty?
  puts "OK: #{skill_names.size} skills, #{agent_count} agents, #{Dir.glob("rules/*.md").size} rules validated."
else
  failures.each { |failure| puts "FAIL: #{failure}" }
  exit 1
end
RUBY
