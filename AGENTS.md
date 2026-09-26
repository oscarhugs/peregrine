# AGENTS.md

Instructions for Codex. This repo is shared between **Codex** and **Claude Code** (Claude reads `CLAUDE.md`, which has the same protocol). State is split so the two agents never edit the same file: **Claude writes only `STATE.md`, Codex writes only `STATE.codex.md`.** Both read both.

## Trigger words

**When the user says "start" (or close to it — "start work", "let's go", "resume"):**
1. Run `git checkout main && git pull` to get the latest state.
2. Read `STATE.md` (Claude's; it holds the **[Codex queue]**) and `STATE.codex.md` (yours).
3. Create a branch for the task: `git checkout -b codex/<short-task-name>`.
4. Give a short summary of what's in progress, what's next, and any relevant notes/decisions — before doing anything else the user asks for.

**When the user says "finish the day" (or close to it — "wrap up", "finish work", "done for today"):**
1. Update **`STATE.codex.md` only** (never edit `STATE.md`):
   - Move finished items from "In progress" to "Done" (with today's date, YYYY-MM-DD).
   - Update "In progress" with anything left mid-flight and where it was left off.
   - Add any decisions worth remembering to "Notes/decisions".
   - Trim "Done" to roughly the last 10–15 entries.
2. Run `git add -A`, `git commit` with a message summarizing the session, then `git push -u origin codex/<short-task-name>` and open a pull request to `main` (`gh pr create --fill` if `gh` is available; otherwise give the user the GitHub compare link). Don't merge it yourself; Oscar reviews and merges.
3. Confirm with a one-line summary: the PR link, and what's next in the queue.

## General session protocol (fallback if the user doesn't use the trigger words)

- At the **start** of any session, read `STATE.md` and `STATE.codex.md` before doing anything else.
- At the **end** of any session, or after a meaningful chunk of work, update `STATE.codex.md` the same way as above, and commit/push the branch if there are changes.
- Keep `STATE.codex.md` short and current — prune stale detail rather than letting it grow forever. It's working memory, not an archive.
- In **Codex cloud** tasks (which end in a PR automatically), still update `STATE.codex.md` in the same PR.

## Working with Claude in this repo

- **Deal Postmortem channel** (`MA Channel/`): Claude owns research, scripts, storyboards, and prompts. Codex owns the code tools under `MA Channel/tools/`. Task briefs are in `MA Channel/tools/*/CODEX_TASK.md`; follow them exactly and read `MA Channel/brand/BRAND.md` for visual rules.
- Don't edit `MA Channel/RESEARCH.md`, `PLAN.md`, `prompts/`, or `videos/*/script.md` unless the user asks; flag needed changes in `STATE.codex.md` instead.
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
