# AGENTS.md

Instructions for Codex. This repo is shared between **Codex** and **Claude Code** (Claude reads `CLAUDE.md`, which has the same protocol). Both agents use `STATE.md` as shared working memory.

## Trigger words

**When the user says "start" (or close to it — "start work", "let's go", "resume"):**
1. Run `git pull` to get the latest state.
2. Read `STATE.md`.
3. Give a short summary of what's in progress, what's next, and any relevant notes/decisions — before doing anything else the user asks for.

**When the user says "finish the day" (or close to it — "wrap up", "finish work", "done for today"):**
1. Update `STATE.md`:
   - Move finished items from "In progress" to "Recently done" (with today's date, YYYY-MM-DD). Prefix Codex entries with `[Codex]` so the user can tell who did what.
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
- In **Codex cloud** tasks (which end in a PR instead of a push), still update `STATE.md` in the same PR.

## Working with Claude in this repo

- **Deal Postmortem channel** (`MA Channel/`): Claude owns research, scripts, storyboards, and prompts. Codex owns the code tools under `MA Channel/tools/`. Task briefs are in `MA Channel/tools/*/CODEX_TASK.md`; follow them exactly and read `MA Channel/brand/BRAND.md` for visual rules.
- Don't edit `MA Channel/RESEARCH.md`, `PLAN.md`, `prompts/`, or `videos/*/script.md` unless the user asks; flag needed changes in `STATE.md` instead.
- Never commit secrets or voice recordings: `.env`, `MA Channel/tools/voice/reference/`, and generated audio are gitignored and must stay that way.

## Response style

- Answer first. No preamble, no recap of the question.
- Number multi-step instructions; cap lists at 5 items.
- Cut filler and closers ("hope this helps", "let me know").
- End with one clear next action when something is pending.
- Longer only when the user asks for detail or the content needs it.

## Coding rules

1. **State assumptions.** If the brief is ambiguous, say what you assumed in the PR description; don't silently pick.
2. **Minimum code.** Solve the brief, nothing speculative. No abstractions for one use. Prefer stdlib and existing code.
3. **Surgical changes.** Touch only files the task needs. No drive-by refactors or reformatting.
4. **Verify explicitly.** Run it, and list in the PR what you ran and what it output.
