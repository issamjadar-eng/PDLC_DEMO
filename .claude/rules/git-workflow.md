# Rule: Commit vs. Push — This Project's Git Workflow

This project does **not** use a typical feature-branch + pull-request-review workflow. There is no human PR review gate. There are effectively **two** git actions, and the user's vocabulary maps onto them.

## The two actions

| User says | Meaning | What Claude does |
|-----------|---------|------------------|
| **"commit"** | Local only. | Stage + `git commit` on the current branch. Nothing leaves the local clone. |
| **"push"**, **"merge"**, **"merge push"**, **"save to repo"**, **"land it"**, **"get it into main"** | Get the work fully merged into `main` on the shared GitHub repo. | The full sequence below. |

When the user says any of the "push" synonyms, they do **not** mean "just push the branch to origin." A branch sitting on `origin` that isn't merged into `main` is **not** "pushed" in this project's vocabulary.

## The "push" sequence

When asked to push / merge / save to repo:

1. **Commit** any outstanding work on the current branch (if not already committed).
2. **Push the branch** to `origin`.
3. **Open a PR** to `main` (`gh pr create`). Write a real summary + test-plan body — the PR is the audit trail, even though no one reviews it.
4. **Merge the PR immediately** (`gh pr merge --merge`). No review gate — do not wait for approval.
5. **Delete the branch** (local + remote) — `gh pr merge --delete-branch` handles both.
6. Confirm to the user that the work is on `main`.

For irreversible or outward-facing steps, the standing "confirm first" guidance still applies — but in this project, merging your own branch to `main` is the *expected* outcome of "push," not a surprise, so a one-line "merging PR #N to main now" is sufficient; you don't need to stop and ask.

## Why a PR at all, if no one reviews it

The PR leaves a durable, linkable record in GitHub history (what changed, when, why) — valuable in a regulated project for audit posture. The cost is one extra `gh` call. So: **PR-then-auto-merge**, not direct commits to `main` and not long-lived branches.

## How to apply

- Hearing "commit" → stop after the local commit. Don't push.
- Hearing "push" / "merge" / "save to repo" / any synonym → run the full 6-step sequence; don't stop at "the branch is in sync with origin."
- If the branch is already merged and clean, say so — don't open an empty PR.
- If `main` has advanced since the branch was cut, a fast-forward pull of `main` during merge is normal; other team members' already-merged work coming along is expected, not an error.
