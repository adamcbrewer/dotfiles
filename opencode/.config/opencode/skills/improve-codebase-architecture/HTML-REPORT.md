# HTML Report Format

Render the architecture review as one self-contained HTML file in the OS temp directory. It must work offline and must not load scripts, styles, fonts, or images from the network.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Architecture review - {{repo name}}</title>
    <style>
      :root {
        color-scheme: light;
        font-family: system-ui, sans-serif;
        color: #0f172a;
        background: #fafaf9;
      }
      body { margin: 0; }
      main { width: min(64rem, calc(100% - 3rem)); margin: 0 auto; padding: 3rem 0; }
      header, article, #top-recommendation { margin-bottom: 2.5rem; }
      article, #top-recommendation { padding: 1.5rem; border: 1px solid #cbd5e1; border-radius: .75rem; background: white; }
      .badges, .files, .wins { display: flex; flex-wrap: wrap; gap: .5rem; }
      .badge { padding: .2rem .55rem; border-radius: 999px; background: #e2e8f0; font-size: .75rem; }
      .diagrams { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }
      .diagram { min-height: 20rem; padding: 1rem; border: 1px solid #cbd5e1; border-radius: .5rem; overflow: auto; }
      .diagram svg { display: block; width: 100%; height: auto; }
      .module { fill: #f8fafc; stroke: #475569; stroke-width: 2; }
      .deep-module { fill: #1e293b; stroke: #0f172a; stroke-width: 4; }
      .seam { stroke: #64748b; stroke-dasharray: 5 5; }
      .leak { stroke: #dc2626; stroke-width: 3; }
      .warning { padding: .75rem; border-left: 4px solid #d97706; background: #fffbeb; }
      code { font-family: ui-monospace, monospace; }
      @media (max-width: 44rem) { .diagrams { grid-template-columns: 1fr; } }
    </style>
  </head>
  <body>
    <main>
      <header>...</header>
      <section id="candidates">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## Content

The header contains the repository name, date, and a compact legend. Each candidate is an `<article>` containing:

- a short title naming the deepening
- recommendation and dependency badges
- a monospaced file list
- side-by-side before and after diagrams
- one sentence each for the problem and solution
- short benefit bullets
- an ADR warning when applicable

End with one top recommendation linking to its candidate.

## Diagrams

Use inline SVG for dependency graphs, call flows, sequences, cross-sections, mass diagrams, and call-graph collapses. Include a `<title>` and `<desc>` in every SVG. Use labelled shapes and arrow markers rather than relying on color alone.

Keep diagrams around 320px tall. Use red only for leakage, amber for warnings, and one accent color for recommendations. On narrow screens, stack before and after diagrams vertically.

## Tone

Keep prose sparse and use the `codebase-design` vocabulary: module, interface, implementation, depth, deep, shallow, seam, adapter, leverage, and locality. Prefer concrete claims tied to files and observed behavior.
