---
name: simplify
description: Simplify recently modified code without changing behavior. Use when the user explicitly asks to simplify, deslop, or clean up code, or when an orchestrator assigns a simplification pass.
source: https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md
---

Simplify recently modified code while preserving exact behavior. Prefer readable, explicit code over compact tricks.

## 1. Preserve Functionality

Never change what the code does - only how it does it. All original features, outputs, and behaviors must remain intact.

## 2. Apply Project Standards

Follow the established coding standards from the codebase guidelines including:

- Follow the repository's language, module, typing, and framework conventions
- Preserve existing error-handling patterns unless they caused the complexity being addressed
- Maintain consistent naming conventions

## 3. Enhance Clarity

Simplify code structure by:

- Reducing unnecessary complexity and nesting
- Eliminating redundant code and abstractions
- Improving readability through clear variable and function names
- Consolidating related logic
- Removing unnecessary comments that describe obvious code
- **IMPORTANT**: Avoid nested ternary operators - prefer switch statements or if/else chains for multiple conditions
- Choose clarity over brevity - explicit code is often better than overly compact code

## 4. Maintain Balance

Avoid over-simplification that could:

- Reduce code clarity or maintainability
- Create overly clever solutions that are hard to understand
- Combine too many concerns into single functions or components
- Remove helpful abstractions that improve code organization
- Prioritize "fewer lines" over readability (e.g., nested ternaries, dense one-liners)
- Make the code harder to debug or extend

## 5. Focus Scope

Only refine code that has been recently modified or touched in the current session, unless explicitly instructed to review a broader scope.

## Refinement Process

1. Identify the recently modified code sections
2. Analyze for opportunities to improve elegance and consistency
3. Apply project-specific best practices and coding standards
4. Ensure all functionality remains unchanged
5. Verify the refined code is simpler and more maintainable
6. Document only significant changes that affect understanding

Do not run this pass unless the user requests it or an orchestrator assigns it.
