---
name: figma-intake
description: Distills an existing Figma design into a self-contained "design spec" handoff that a downstream planner (the designer agent / ui-ux-plan) can consume — screenshots, component list, design tokens/variables, and Code Connect mappings — so the design becomes the visual source of truth without passing a bare Figma URL to a sub-agent. Use when a feature comes with a Figma design and you need to feed it into a planning/implementation pipeline, or whenever you want a clean, text+image spec extracted from a Figma frame. Triggers on "I have a Figma design", "extract this Figma", "pull the design from Figma", "feed this Figma into the pipeline/designer". MUST run where the Figma MCP is available (the main/top-level session) — not inside a sub-agent that can't reach the Figma MCP. Not for generating designs INTO Figma (use figma-generate-design) or implementing Figma directly to production code.
---

# Figma Intake

Turn an existing Figma design into a **distilled design spec** — a self-contained
artifact (screenshots + components + tokens + any code mappings) that a downstream
planner can treat as the visual source of truth. The point is to do the Figma
reading *once, here*, and hand forward a clean spec — so a sub-agent (e.g. the
`designer`) never needs to reach Figma itself.

> **Runs where the Figma MCP lives — the main/top-level session.** Sub-agents
> can't reliably reach the Figma MCP, and the mandatory figma-skill prerequisites
> (`figma-use` before `use_figma`, etc.) apply. If you don't have the Figma tools,
> stop and say so rather than guessing at the design.

## When to use

- A feature arrives with a Figma design and you're about to plan/build it (feeding
  the orchestration pipeline / the `designer`).
- You want a clean, reusable text+image spec pulled from a Figma frame for any
  downstream reasoning.

**Don't use** for: generating a design *into* Figma (`figma-generate-design`),
implementing a Figma file straight to production code, or when no real design
exists yet (then the designer designs from scratch — skip this).

## Process

1. **Scope to a specific frame/node, not the whole file.** If the user gave only a
   file URL, ask them to point at the frame(s) that matter so the extract stays
   focused and the spec is sharp.
2. **Load the figma skills as their prerequisites require**, then gather:
   - `get_screenshot` — the visual(s) of the frame(s). The anchor of the spec.
   - `get_design_context` / `get_metadata` — structure, layers, and the components
     in use.
   - `get_variable_defs` — design tokens/variables (color, spacing, type, radius).
     Capture exact names so the plan reuses them verbatim.
   - `get_code_connect_map` — **if the repo has Code Connect**, this maps Figma
     components → real code components. Pull it; it turns the downstream
     reuse/extend/new tagging from inferred into precise.
3. **Note what Figma doesn't tell you.** A static frame rarely shows loading/empty/
   error/permission states, responsive behavior, interaction/motion, or real-data
   edge cases. Flag these as gaps the downstream planner must complete — don't
   invent them here.

## Output — the design spec

Produce one self-contained artifact:

```markdown
# Design Spec (from Figma): [surface]

**Source** — [frame/node reference]
**Screens** — [the screenshot(s); one per state/breakpoint captured]

## Components in the design
| Element | Figma component | Code Connect → code component (if any) |

## Tokens / variables
[color, spacing, type, radius — exact names from get_variable_defs]

## Layout & hierarchy
[Structure, sections, what draws the eye — read from the frame, not invented.]

## Gaps Figma doesn't specify (for the planner to complete)
[States not shown · responsive behavior · interactions/motion · edge cases.]
```

Hand this spec to the downstream consumer (the `designer` / `ui-ux-plan`) as the
**visual source of truth**, with the instruction to *translate → reconcile with the
codebase → complete the gaps* — not to redesign it.

## Principles

- **Read once, hand forward.** Do the Figma extraction at the layer that can reach
  Figma; pass a distilled spec downward, never a bare URL.
- **Exact names, not approximations.** Capture token and component names verbatim so
  the plan translates to code with no guessing.
- **Code Connect makes it precise.** When present, use it — inferred mappings are a
  fallback, not the goal.
- **Name the gaps, don't fill them.** Flag what the static design omits; completing
  states/responsive/a11y is the downstream planner's job.
- **The design is truth, not a suggestion.** Extract faithfully; reconciliation and
  divergence calls happen downstream, surfaced as decisions.
