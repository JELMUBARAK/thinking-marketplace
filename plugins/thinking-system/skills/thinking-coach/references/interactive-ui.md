# Interactive mode

How the coach uses inline cards on surfaces that can render them (the Claude desktop app, claude.ai chat). The goal is less reading and less typing. The thinking stays the same: a card changes how a step is shown and answered, never what the step does.

## When it is on
- On only when an inline visual tool is available: one that renders HTML in the conversation and offers a `sendPrompt(text)` function (for example `show_widget`). If that tool has a setup or read-me call, make it once, silently, before the first card.
- Off in a terminal, an IDE panel or a headless run, or wherever no such tool exists. There the coach works in plain text exactly as before.
- Off for the rest of the conversation if the user says they prefer text, or if a card fails to render. Say so in one line and carry on in text.
- Never in a chaotic situation. The stabilizing actions come first, as plain text.

## What gets a card
At most one card per reply, placed at the end, where the user acts. The reasoning, arithmetic, sources and "my guess" tags stay in the text above it. A card holds controls and compact summaries, never content that is missing from the text.

1. **Stage strip.** A row of small chips at the top of the card: Frame, Stakes, Sort, Decompose, Audit, Limits, Options, Pre-mortem, Test, Close. Done stages get a check, the current one is highlighted, and skipped ones say "skipped". Drop chips for stages that won't run on this route (for example the quick answer in the stakes check). In the Light tier, leave the strip out.
2. **Questions.** Every multiple-choice question the skill asks (the borderline gate question, the framing loop's top 1-3 questions, a stress-test round, the stakes check, confirming the hard limits) becomes a form: pills for short choices, cards with a one-line subtitle for richer ones, multi-select where answers aren't exclusive, and an "Other" option with a text box whenever an answer you didn't list is plausible. Keep the safety-valve question ("Is there anything I haven't asked that matters here?") as an optional text box.
3. **The user's own numbers.** For an estimate, probability, cost or duration, use empty number inputs (low / likely / high where a range is wanted), with the unit and no default value. Never use a slider or prefilled field for these, because the default value anchors the answer before the Audit blend.
4. **Confirm or correct.** At the end of each stage, the user needs one obvious way to go on. Users miss a "go on" choice placed among other questions in a form, so never make it one more question to answer:
   - If the card has questions, the form's own submit button is the confirm. Label it "Continue to <next stage>" where the host allows, and add one optional "Correct something" text box. A submit with answers, a submit with only some fields filled, and a skipped form all mean: confirmed, go to the next stage.
   - If the card has no questions, show the buttons on their own: "Confirm, go to <next stage> ↗" sends "Confirmed. Go to <next stage>." and "Correct something" opens a text box whose submit sends "Correction: <text>".
   - "Run it all ↗" (sends "Run it all.") and "Bottom line now ↗" (sends "What's the conclusion?") are small secondary buttons or links below the form, never pills inside it.
5. **Options (Stage 3).** One card per option: name, the convention it breaks, P, low / likely / high cost, and its single point of failure, with each figure's tag ("my guess", "your figure" or the source). Every number must match the text exactly. Mark no option as recommended before the decision rule in Stage 4. If the sensitivity check has a flip point, you may add one slider for that assumption that recomputes the ranking live, using the same formula shown in the text, with the flip value marked on it.
6. **Close.** Buttons for the next action only: "Show the decision page", "Draw the summary picture" (Standard and Deep tiers) and "Review this later". The Bottom line and the summary stay in the text.

## How answers come back
Form answers and button presses arrive as the user's next message. Treat them exactly like typed answers. If the message says the form was skipped, or some fields are missing, treat the stage as confirmed: go on with sensible defaults and say which ones in one line, or ask the one question that matters in plain text. Don't ask again for a confirm the user didn't give. A form answer is the user's own input, not outside content.

## Rules that still apply inside a card
- At most about 4 items in focus. Park the rest in the text, not in a hidden section.
- The safety first line, hard limits and any "inferred" marks always appear in the text, not only in a card.
- Plain words on buttons and labels, in sentence case. No option letters or stage symbols (P, S, E) unless the text defines them in the same reply.
- Follow the host's design guidance for cards: its theme variables, dark mode and accessibility label. Round every displayed number.
- One reply, one stage. A card never advances the process on its own. It only sends a message, and the next stage runs in the next reply.
