# CLAUDE.md

## Session protocol

**Start of every session:** read `STATE.md` before doing anything else, including before answering the first request. It is the source of truth for what's in progress, what's next, and past decisions.

**End of every session** (or when the user wraps up / a meaningful chunk of work finishes), update `STATE.md`:
- Move finished items from "In progress" to "Recently done" (with the date, YYYY-MM-DD).
- Update "In progress" to reflect what's actually mid-flight, including where it was left off.
- Update "Next up" with the concrete next steps.
- Add any decisions worth remembering (and why) to "Notes/decisions".
- Trim "Recently done" to roughly the last 10–15 items so the file stays short.

Keep entries brief — one line each where possible.
