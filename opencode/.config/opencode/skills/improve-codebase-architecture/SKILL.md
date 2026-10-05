---
name: improve-codebase-architecture
description: Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one the user picks. Use only when the user explicitly requests an architecture review.
source: https://github.com/mattpocock/skills/blob/main/skills/engineering/improve-codebase-architecture/SKILL.md
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

Use the project's terminology and existing architecture decisions. A **deep module** hides substantial complexity behind a small interface; a **shallow module** exposes nearly as much complexity as it implements. A **seam** is where a dependency can be replaced, and an **adapter** is an implementation of that dependency's interface.

Prefer changes that simplify callers, concentrate related behavior, and can be tested through the module's interface. Introduce dependency interfaces where something actually varies, rather than creating hypothetical abstractions.

## Process

### 1. Explore

**Scope before you scan — YAGNI.** Deepening a module pays off by making future changes to it easier, so put extra weight on the parts of the codebase that have recently changed. Decide _where_ to look before you look:

- If the user named a direction — a module, a subsystem, a pain point — take it, and skip the inference below.
- Otherwise, walk back a good stretch of the commit history (`git log --oneline`) to find the codebase's hot spots — the files and areas that keep coming up — and let those paths pull your attention first. If the changes are scattered with no clear hot spot, widen the net.

Read existing project documentation, any glossary (`GLOSSARY.md` or `CONTEXT.md`), and relevant ADRs first. Do not require or create glossary files for the review.

Then use the Task tool with `subagent_type=explore` to walk the codebase. Don't follow rigid heuristics — explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want.

### 2. Present candidates as an HTML report

Write a self-contained HTML file to the OS temp directory so nothing lands in the repo. Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows), and write to `<tmpdir>/architecture-review-<timestamp>.html` so each run gets a fresh file. Open it for the user using the platform's standard command and tell them the absolute path.

The report must work offline. Use embedded CSS and inline SVG only; do not load scripts or other assets from CDNs. Each candidate gets a visual before-and-after comparison.

For each candidate, render a card with:

- **Files** — which files/modules are involved
- **Problem** — why the current architecture is causing friction
- **Solution** — plain English description of what would change
- **Benefits** — how callers become simpler, related behavior stays together, and tests improve
- **Before / After diagram** — side-by-side, custom-drawn, illustrating the shallowness and the deepening
- **Recommendation strength** — one of `Strong`, `Worth exploring`, `Speculative`, rendered as a badge

End the report with a **Top recommendation** section: which candidate you'd tackle first and why.

**Use the project's domain terms.** If the project calls something an "Order," use that term rather than an incidental implementation name such as "FooBarHandler."

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly in the card (e.g. a warning callout: _"contradicts ADR-0007 — but worth reopening because…"_). Don't list every theoretical refactor an ADR forbids.

See [HTML-REPORT.md](HTML-REPORT.md) for the full HTML scaffold, diagram patterns, and styling guidance.

Do NOT propose interfaces yet. After the file is written, ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, load the `grilling` skill to walk the decision tree with them — constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

When decisions crystallize:

- **User rejects the candidate with a lasting, non-obvious reason?** Offer to record an ADR using the project's conventions so future reviews do not re-suggest it. Write it only if the user agrees.
- **Want to explore alternative interfaces for the deepened module?** Use parallel sub-agents with different constraints: minimize the interface, maximize flexibility, and optimize for the most common caller. Give each the same files, constraints, and dependencies. Compare their interfaces, hidden complexity, dependency strategies, and trade-offs, then recommend a design.
