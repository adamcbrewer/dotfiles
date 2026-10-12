# Mention-triggered Codex diff explainer

This experiment uses a project's GitHub workflow to forward your PR mention to
the connected Codex integration. GitHub Actions posts the request. If Codex
accepts it, the cloud integration handles the subscription-backed analysis.

**Unverified:** OpenAI documents user-authored `@codex` tasks, but does not
guarantee that Codex accepts requests from `github-actions[bot]`. A successful
workflow run proves the request was posted, not that Codex ran it.

## Add it to a project

1. Copy [the workflow template](workflows/codex-diff-explainer.yml) into the
   project's `.github/workflows/codex-diff-explainer.yml`.
2. Copy the complete
   [`diff-explainer` package](../agent-skills/.agents/skills/diff-explainer/)
   into the project's `.agents/skills/diff-explainer/`, including `references/`
   and `agents/`. Use reviewed copies committed with the project; local Stow
   links do not transfer to Codex cloud.
3. Make both available on the project's default branch. `issue_comment`
   workflows are loaded from that branch, and the template checks its skill
   files there before forwarding a request.
4. Confirm the project is connected to Codex and has a cloud environment for
   GitHub-triggered tasks. The template uses GitHub's built-in `GITHUB_TOKEN`;
   it needs no additional token secret.

By default, only the repository owner's GitHub account can request an
explanation. For an organisation repo or a different linked account, set the
repository variable `CODEX_REQUESTER` to that account's GitHub login.

The template uses the runner's preinstalled Python and GitHub CLI. It reads
repository metadata and posts comments without checking out or executing PR
code.

## Request an explanation

Post this as a standalone comment on a pull request:

```text
@diff-explainer
```

This is a workflow command string. The workflow posts an expanded
`@codex explain ...` comment with the skill path, PR link, base/head commits,
diagram instructions, and a request to return the Markdown report to the PR
when commenting access is available. Bot replies and unrelated comments do
not forward requests. Rerunning the same comment's job reuses its existing
forwarded request; post a new mention to request a fresh explanation.

For Codex's built-in findings review, use `@codex review` separately.

## Check the experiment

1. Confirm **Request Codex diff explanation (experiment)** runs and posts the
   expanded request. Its log includes the new comment URL.
2. Look for a Codex reaction, task link, or response to that bot-authored request.
3. Open the task and check that it reads the skill and diagram reference, compares
   the supplied commits, and produces Mermaid only when the change warrants it.
4. Confirm whether the report was posted to the PR or returned only in the task.

If Codex ignores the bot, copy its expanded request into a comment from your
linked GitHub account. That tests the documented user-mention path using the
same prompt. Bot forwarding remains unconfirmed until Codex actually responds.

For an existing CI YAML, the same job can be added alongside `issue_comment`
under `on`. Existing build/test jobs need event guards so PR comments do not
start those jobs too. A separate workflow file is easier for this experiment.

References: [Codex GitHub integration](https://developers.openai.com/codex/third-party/github/),
[GitHub `issue_comment` events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#issue_comment),
and the repository's [setup security guidance](https://github.com/lirantal/npm-security-best-practices).
