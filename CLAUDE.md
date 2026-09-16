# Global preferences

- Automated multi-agent flows run in the current working tree, one writing stage
  at a time. The orchestrator owns sequencing, artifact handoff, diff inspection,
  and verification; workers read only their assigned inputs and write only their
  assigned output.
- Never create branches, worktrees, or commits, and never write commit messages.
  Never push, open a PR, or deploy. If the user wants any of that, they ask for it
  explicitly. Read-only git (`status`, `diff`, `log`, `blame`) is always fine.
- Before an automated run, note the changes already in the tree so the run's own
  diff stays attributable. Never revert, stash, discard, or overwrite user work to
  recover from a problem — stop and report instead.
- Never read the 'node_modules' dir unless you really need to debug something related.
- If you see something was deleted by the user - do not restore it. Consider that an intentional fix.
- If there is a problem with bundler or gems - check for the '.ruby-gemset' file. Most probably all gems are installed in the gemset dir.
- Store artifacts, scratch outputs, and logs under the project-relative
  `.claude/tmp/` dir, grouped by task. Keep all scratch out of tracked source and
  `docs/`.
