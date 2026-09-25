# CLAUDE.md

## Trigger words

**When the user says "start" (or close to it — "start work", "let's go", "resume"):**
1. Run `git pull` to get the latest state.
2. Read `STATE.md`.
3. Give a short summary of what's in progress, what's next, and any relevant notes/decisions — before doing anything else the user asks for.

**When the user says "finish the day" (or close to it — "wrap up", "finish work", "done for today"):**
1. Update `STATE.md`:
   - Move finished items from "In progress" to "Recently done" (with today's date, YYYY-MM-DD).
   - Update "In progress" to reflect anything left mid-flight, including where it was left off.
   - Update "Next up" with concrete next steps for the following session.
   - Add any decisions worth remembering to "Notes/decisions".
   - Trim "Recently done" to roughly the last 10–15 entries.
2. Run `git add -A`, then `git commit` with a message summarizing the session's work, then `git push`.
3. Confirm with a one-line summary of what was committed/pushed and what's queued up for next time.

## General session protocol (fallback if the user doesn't use the trigger words)

- At the **start** of any session, read `STATE.md` before doing anything else.
- At the **end** of any session, or after a meaningful chunk of work, update `STATE.md` the same way as above, and commit/push if there are changes.
- Keep `STATE.md` short and current — prune stale detail rather than letting it grow forever. It's working memory, not an archive.
