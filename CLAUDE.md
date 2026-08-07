# Global preferences

- Do not commit, push, switch git branch or make a PR unless you are explicitly asked to do so.
- Never read the 'node_modules' dir unless you really need to debug something related.
- If you see something was deleted by the user - do not restore it. Consider that an intentional fix.
- If there is a problem with bundler or gems - check for the '.ruby-gemset' file. Most probably all gems are installed in the gemset dir.
- Store all intermediate data, scratch outputs, and logs under the project-relative `.claude/tmp/` dir — group a task's files in a subdir, e.g. `.claude/tmp/<task-slug>/`. Create it if it doesn't exist. Keep this scratch out of the tracked source tree and out of `docs/`; the working tree stays clean unless I'm explicitly asked to keep an artifact.
