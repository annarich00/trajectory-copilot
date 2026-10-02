# Atomic task commit policy

Every Backlog task must finish as one discoverable, independently reviewable, and revertible Git commit.

## Per-task workflow

1. **Start clean.** Before task work, update the intended base and confirm `git status --short` is empty. Do not mix pre-existing or unrelated changes into the task.
2. **Isolate the task.** Work only on the selected task's implementation, tests, documentation or site updates, and Backlog metadata. One task maps to one atomic commit.
3. **Use isolation for parallel work.** Each concurrently active task must use its own branch and worktree. Do not share a working tree between parallel tasks; integrate each task commit independently.
4. **Verify the task.** Run the relevant automated tests and repository checks. When an educational site exists, also run its documented site checks. Record exact outcomes in the Backlog task.
5. **Finalize Backlog.** Read the task-finalization instructions, verify and check every acceptance criterion and Definition of Done item with objective evidence, add implementation notes and a final summary, and mark the task Done.
6. **Create one discoverable commit.** The commit subject must begin with the exact task ID followed by a colon: `<task-id>: <summary>` (for example, `TJC-1.26: establish atomic task commits`). Include only that task's implementation, tests, documentation/site changes, and finalized Backlog metadata.
7. **Amend, never add bookkeeping commits.** If task-finalization metadata is written after the initial task commit, stage it and use `git commit --amend` so it becomes part of the same task commit. Do not create a separate metadata or bookkeeping commit.
8. **Finish clean.** Confirm the final commit contains no unrelated files, generated process artifacts, credentials, or secrets; rerun applicable checks if the amend affected them; then confirm `git status --short` is empty.

## Initial checkpoint

TJC-1.26 is the repository's initial pre-site checkpoint. It includes the recovered baseline and represents TJC-1.1, which predates Git history and is not rewritten retroactively. The educational site is intentionally absent from this checkpoint. TJC-1.25 must backfill the TJC-1.26 task/commit entry when the living progress page is established.
