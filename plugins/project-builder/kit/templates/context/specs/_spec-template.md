# Unit NN: [Unit Name]

Branch: `feat/NN-unit-name`
Depends on: [unit numbers, or none]

## Goal

[One or two sentences: the concrete result of this unit.
Bad: "Create the auth pages."
Good: "Create sign-in and sign-up pages using Clerk components. Desktop has a two-panel layout and mobile shows the form only. Routes are protected with proxy.ts."]

## Design

[Visual or output decisions for this unit. Reference ui-context.md tokens or the Output contract.
Describe layout, responsiveness and output format. Leave nothing for the agent to guess.]

## Implementation

### [Component / sub-section name]

[Exactly what to build and how.]

### [Next sub-section]

[Description.]

## Out of scope for this unit

- [Things this unit must NOT touch, even if they look related]

## Dependencies

- [package-name (reason)], or "None"

## Verify when done

- [ ] [Specific condition one]
- [ ] [Specific condition two]
- [ ] The verify command from architecture.md passes (paste its output)
- [ ] No invariant from architecture.md was broken
- [ ] [Type checks from the type add-on in context/kit/, e.g. responsive at mobile and desktop / evals not worse
      than the previous version / pytest green]
