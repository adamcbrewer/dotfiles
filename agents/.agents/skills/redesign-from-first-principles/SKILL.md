---
name: redesign-from-first-principles
description: Redesign an existing solution around a new requirement as if it had been foundational. Use only when the user explicitly invokes redesign-from-first-principles.
license: MIT
source: https://github.com/cursor/plugins/blob/main/pstack/skills/principle-redesign-from-first-principles/SKILL.md
disable-model-invocation: true
---

# Redesign From First Principles

When explicitly requested, integrate a change by redesigning as if the requirement had been there from the start. The result should look like what we would have built if we'd known on day one.

- Read all affected files and understand the current design holistically
- Ask: "if we were writing this from scratch with this new requirement, what would we build?"
- Propagate the change through every reference: types, docs, examples, rationale sections
- Think about the redesign holistically, then deliver it incrementally

This is the method for preserving option value when integrating changes into an existing design.
