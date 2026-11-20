# Concept types and routes

The type changes what the mechanism looks like, what the Why lens asks, and which route the gate picks.

## Types
| Type | Test | Mechanism shape | Why lens asks for |
|---|---|---|---|
| physical | Made of matter or energy; behaves the same whatever people believe | states, transitions, driver, gradient, resistance, thresholds | energy source (driver), gradient, resistance |
| formal | A rule system: maths, logic, code, statistics; true by definition or proof | rule, invariant, termination / base case, steps of rule application | rule, invariant, termination |
| social-normative | Exists because people agree it does; has purposes and incentives | actors, purpose(s), rules, incentives, transitions, thresholds | purpose, incentive, resistance |

Notes:
- **No driver is a valid answer.** Some physical tendencies are statistical, not pushed (entropy rises because there are vastly more disordered arrangements, not because a force pushes). Write `driver: none (statistical)`. A candidate that imports a driver here makes a false import.
- **Biology** is physical, but often has purpose-like language ("the immune system wants to..."). Use physical mechanism terms; treat purpose language as shorthand only.
- **Mixed** concepts (p-values are formal tools used in a social practice) take the type of what is being explained. Explaining what a p-value *is*: formal. Explaining why journals misuse it: social-normative.

## Routes
| Route | When | What gets built |
|---|---|---|
| `direct_simulation` | The concept is a human-scale thing the learner can see (a kettle, a bicycle gear) | No analogy. Simulation spec of the real thing + what-if quiz. |
| `simulate_first` | Formal concept with an executable rule (recursion, p-values, sorting) | Simulation spec always (the primary model). The machine analogy supports it and is shown only if it passes. |
| `analogy` | Default for settled physical and social concepts | Rule table matched to one machine from `machines.md`, tested on hidden what-ifs. |
| `contested` | Facts status is contested at the layer being explained | One machine per leading model (max 3), labelled "competing, unproven", each shown after one finding it cannot explain. No pick. |
| `values` | The disagreement is about what the word should mean or what is good | One machine per definition (max 3), each attributed. No pick. Never choose the "most likely" meaning when that would take a side. |
| `reject` | Decided after the hidden test: nothing passes after one rule fix | Partial matches, a plain "no everyday machine does X" line, and a simulation spec. |

"Visible" means human-scale and seeable without instruments. A cell is not visible. An engine with the cover off is.

## Prerequisites
List the 1-3 ideas the learner must already hold for any model of this concept to work (p-value needs "probability" and "sample"; recursion needs "function"). If the learner's world suggests they lack one, flag it in the record; the learner layer (Phase 3) will teach it first.

## Default learner domains
Used when the learner's world is unknown. Draw candidates from these, plus at most one unconventional domain per run.
kitchen and cooking; roads and traffic; money and shopping; sport and games; water and plumbing; weather; school and queues; phones and apps; gardening; workplace and offices; post and parcels; building and DIY.
(Open decision for the user: keep a fixed list or ask each learner once. Phase 1 uses this list.)

## Safety topics
Health, money, law, politics. Phase 1 default (pending the user's decision): allowed, but every mapped fact must be tier 1-3, the record gets `"safety_topic": true`, and political topics always take the `values` route if any definition is disputed.
