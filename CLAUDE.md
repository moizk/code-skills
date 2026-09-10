# Global preferences

- Automated multi-agent flows use a dedicated integration branch plus an isolated
  branch and worktree for every agent. The orchestrator owns worktree creation,
  local stage commits, merges, verification, and cleanup.
- Start an automated integration only from a clean working tree. Stop on merge
  conflicts or a changed base; never discard or overwrite user work to recover.
- Outside an orchestrated flow, do not create branches or commit unless explicitly
  asked. Never push, open a PR, deploy, or perform destructive conflict resolution
  unless explicitly asked.
- Never read the 'node_modules' dir unless you really need to debug something related.
- If you see something was deleted by the user - do not restore it. Consider that an intentional fix.
- If there is a problem with bundler or gems - check for the '.ruby-gemset' file. Most probably all gems are installed in the gemset dir.
- Store artifacts, scratch outputs, and logs under the project-relative
  `.claude/tmp/` dir, grouped by task. Linked worktree directories are the one
  exception: place them in a project-adjacent temporary root recorded in the run
  manifest, never inside the user's working tree. Keep all scratch out of tracked
  source and `docs/`; clean successful worktrees when the run finishes.
