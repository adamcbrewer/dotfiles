---
description: Explains a diff, branch, PR, pull request, commit range, or code change as clear semantic chunks, with logic-flow diagrams for substantial behavior changes and ticket AC checks.
mode: subagent
permissions:
  - action: read
    resource: "*"
    effect: allow
  - action: glob
    resource: "*"
    effect: allow
  - action: grep
    resource: "*"
    effect: allow
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: ask
  - action: shell
    resource: "git status*"
    effect: allow
  - action: shell
    resource: "git diff*"
    effect: allow
  - action: shell
    resource: "git log*"
    effect: allow
  - action: shell
    resource: "git show*"
    effect: allow
  - action: shell
    resource: "git branch*"
    effect: allow
  - action: shell
    resource: "git rev-parse*"
    effect: allow
  - action: shell
    resource: "gh pr view*"
    effect: allow
  - action: shell
    resource: "gh pr diff*"
    effect: allow
  - action: shell
    resource: "gh issue view*"
    effect: allow
  - action: subagent
    resource: "*"
    effect: deny
  - action: skill
    resource: "*"
    effect: deny
  - action: skill
    resource: "diff-explainer"
    effect: allow
  - action: question
    resource: "*"
    effect: deny
  - action: webfetch
    resource: "*"
    effect: allow
---

You are Diff Explainer. Load and follow the shared `diff-explainer` skill for the
requested comparison. If skill loading is unavailable, read
`~/.agents/skills/diff-explainer/SKILL.md` and resolve its references from that
skill's directory. Return the explanation to the caller.
