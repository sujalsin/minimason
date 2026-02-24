# 🎬 MiniMason — Loom Demo Script

**Target length**: 2–3 minutes
**Audience**: Michael Aspinwall, Mason engineering team
**Tone**: Professional but genuine — "I built this because I read everything you wrote and it resonated."

---

## INTRO (15 seconds)

> "Hi Michael — I'm [Name]. I built something I wanted to show you. It's called MiniMason, and it's a working prototype that demonstrates how I think about the exact problems you described in your 'LLM Communications in the Wild' post."

*(Share screen showing MiniMason loaded with the dark gradient header visible)*

---

## THE 2 AM SCENARIO (45 seconds)

> "Let's start with the scenario that stuck with me most — the clogged toilet at 2 AM with the blurry photos."

1. Select **Scenario 1: Clogged Toilet Overflow (2 AM)** from the dropdown
2. Point out the panicked, emotional, typo-filled tenant message
3. Click **Process**
4. While loading: *"What I built here does exactly what you described — it takes this messy, emotional input and produces something a property manager can actually act on."*

> "Look at the output: a structured work order with the right severity — HIGH, not EMERGENCY, because there's no electrical proximity. The tenant reply is suave and gentle, just like you described. And notice — it gives them a specific action they can take right now: turn the shut-off valve clockwise."

---

## RED FLAG DETECTION (30 seconds)

> "Now here's where it gets interesting. Let me show you Scenario 10 — this is the 'maximum red flags' request."

1. Select **Scenario 10: Rent Frustration + Bundled Requests**
2. Click **Process**
3. Point out the red flags: frustration escalation, scope creep, vendor upsell

> "The system detects the rent withholding threat, the bundled requests that should be separate work orders — what you called 'unit-of-work integrity' — and the brother-is-a-plumber vendor upsell. It flags all of these for the property manager without being accusatory to the tenant."

---

## GENTLE SKEPTICISM (20 seconds)

> "One more — Scenario 5, the self-diagnosis. Tenant watched a YouTube video and wants to order a specific garbage disposal and install it themselves."

1. Show the output
2. Point out how the reply diplomatically redirects without being condescending

> "This is the gentle skepticism you wrote about — acknowledging their research while making sure a professional verifies the fix."

---

## TECHNICAL DEPTH (20 seconds)

> "Under the hood, this runs on Gemini 2.5 Flash with a 2,500-word system prompt that encodes your severity classification table, your tone calibration rules, image analysis instructions for those blurry 2 AM iPhone photos, and the exact red flag patterns you identified."

*(Briefly scroll through the raw JSON to show the structured output)*

---

## THE CLOSE (20 seconds)

> "I built this because your writing about showing up in person — 'Being There' — resonated with me. Everything great comes from sitting with real operators and building together. This prototype is me showing up with something concrete, the way you did in Sacramento."

> "I'd love to grab 20 minutes to talk about how I could contribute to what you're building at Mason. Thanks for your time."

---

## RECORDING TIPS
- Record at 1080p minimum
- Keep the browser zoomed to ~90% so the full layout is visible
- Use a clean desktop background
- Speak at a natural pace — don't rush
- Total time should be under 3 minutes
