# Build Plan

Approved at STEPS.md Step 8 on: [date]. No code is written before this date.

## Unit rules

- Each unit produces **one visible result you can check**.
- Each unit stays within **one system boundary**.
- A unit can be finished in **one focused session**.
- Install dependencies **just in time**, in the unit that first needs them.
- Merge units that are always done together. Merge units that have no result of their own.

## Ordering rules

1. Dependencies first
2. Security and access before the features they protect
3. Backend before UI wiring
4. UI shells with placeholder data before real data
5. Packages installed only when first needed

## Units

| #  | Unit | Builds (the result you can see) | Depends on | Status |
| -- | ---- | ------------------------------- | ---------- | ------ |
| 01 | [name] | [what it produces] | none | not started |
| 02 | [name] | [what it produces] | 01 | not started |
| 03 | [name] | [what it produces] | 01, 02 | not started |

Status values: `not started`, `spec written`, `spec approved`, `in progress`, `verifying`, `complete`.
