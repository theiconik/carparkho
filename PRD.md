# PRD: Car Recommender (MVP)

**Owner:** [Product]
**Status:** Draft for engineering handoff
**Last updated:** April 20, 2026

---

## 1. Problem

Buyers land on the platform with too many options and no easy way to narrow down. They don't know specs, body types, or tradeoffs — they know their life (family size, commute, budget). The MVP translates life context into a trustworthy shortlist.

## 2. Goal

Take a confused buyer from landing page to a ranked shortlist of **3 cars** in under 2 minutes, with a clear explanation of why each car was picked.

## 3. Non-goals (MVP)

- No chatbot / free-text input
- No used cars — new cars only
- No EMI calculator, trade-in, or test drive booking
- No user accounts / saved shortlists
- No comparison tool beyond the 3 recommended cars
- No post-shortlist refinement or "ask follow-up questions" flow

## 4. User flow

1. User lands on homepage, clicks **"Help me find a car"**
2. Answers 7 questions (one screen per question)
3. Sees a loading state while the system filters and ranks
4. Lands on a results page with top 3 cars, each with:
   - Car image, name, on-road price
   - 2–3 line explanation of why it matched
   - Key specs (seating, fuel type, transmission, safety rating, mileage)
   - Link to the existing car detail page on the platform

## 5. The 7 questions

| # | Question | Input type | Required |
|---|----------|------------|----------|
| 1 | What's your budget? | Dual-handle slider (comfortable at / stretch to) + on-road/ex-showroom toggle | Yes |
| 2 | Who's usually in the car? | Single-select, 5 options | Yes |
| 3 | Where does this car mostly live? | Multi-select, max 2, 5 options | Yes |
| 4 | What would make you regret this purchase in 2 years? | Multi-select, max 3, 7 options | Yes |
| 5 | Fuel preference? | Single-select, 5 options (incl. "no preference") | Yes |
| 6 | Transmission? | Single-select, 3 options | Yes |
| 7 | Anything non-negotiable? | Multi-select chips, optional | No |

Exact option text is defined in `questions-config.json` (see §8).

## 6. Recommendation logic

### Step 1: Hard filter
Remove any car that fails:
- On-road price > user's stretch budget
- Seating capacity insufficient for Q2 answer
- Fuel type mismatches Q5 (unless "no preference")
- Transmission mismatches Q6 (unless "either")
- Missing any non-negotiable feature from Q7

### Step 2: Score remaining cars (0–100)
Weighted scoring across these dimensions. Weights shift based on Q3 and Q4 answers.

| Dimension | Default weight | Boosted when |
|-----------|---------------|--------------|
| Price fit (closer to comfortable budget = higher) | 20 | Always |
| Safety rating | 15 | Q4 includes "didn't feel safe" |
| Space & practicality | 15 | Q2 = family/household OR Q4 includes "cramped" |
| Ground clearance / ride quality | 10 | Q3 includes "bad roads" or "hills/rain" |
| Fuel economy / running cost | 10 | Q4 includes "expensive to run" |
| City maneuverability (size, turning radius, visibility) | 10 | Q3 includes "dense city" |
| Highway capability (power, comfort) | 10 | Q3 includes "highways" |
| Reliability / brand trust | 5 | Q7 includes "reliable brand" |
| Resale value | 5 | Q4 includes "depreciated" OR Q7 includes "resale" |

Return the **top 3 scored cars**.

### Step 3: Generate explanation
For each of the 3 cars, call the LLM **once** with:
- User's 7 answers
- The car's specs
- The top 3 dimensions where this car scored highest

Prompt returns 2–3 sentences explaining the fit in plain language.

**Why this approach:** Deterministic filtering + scoring keeps the core recommendation explainable and testable. LLM is used only for natural-language explanation — no hallucination risk on specs or prices.

## 7. Edge cases

- **Fewer than 3 cars pass the hard filter:** Show whatever passes (1 or 2 cars) with a banner: *"Only X cars matched your must-haves. Adjust your preferences to see more."* with a "Start over" button.
- **Zero cars pass the hard filter:** Show an empty state: *"No cars match all your requirements. The most common blocker was [budget / non-negotiables / fuel type]."* with a "Start over" button. Identify blocker by re-running filter without each constraint and seeing which unlock produces results.
- **LLM explanation fails or times out (>3s):** Fall back to a template: *"This car matched your preferences for [top 3 dimensions]."*
- **User navigates back mid-flow:** Preserve previous answers. Do not reset.

## 8. Data & config

- **Car dataset:** Use existing platform DB. Required fields per car: make, model, variant, on-road price (by city — default to Bengaluru for MVP), ex-showroom price, seating capacity, fuel type, transmission, body type, safety rating (stars), mileage, ground clearance, boot space, key features list, image URL, detail page URL.
- **Questions config:** Store in `questions-config.json` so copy can be updated without deploys.
- **Scoring weights:** Store in `scoring-config.json` for tuning post-launch.

## 9. Tech notes

- **Frontend:** Single-page flow, mobile-first. One question per screen. Progress indicator (1/7, 2/7…).
- **Backend:** Filter + score runs server-side. LLM call is server-side only (never expose key to client).
- **LLM:** One call per session, generating 3 explanations in a single structured prompt (not 3 separate calls). Target latency <3s. Use `claude-haiku-4-5` for speed/cost.
- **Analytics:** Track drop-off per question, final shortlist shown, and click-through to detail page.

## 10. Success metrics

- **Completion rate:** % of users who start the flow and reach results — target 60%+
- **Click-through rate:** % of users on results page who click into at least one detail page — target 50%+
- **Time to shortlist:** Median time from Q1 to results page — target under 2 minutes

## 11. Out of scope (explicitly deferred)

Follow-up conversational refinement, "compare these 2" flow, saving shortlists, used cars, EMI, trade-in, dealer connect, test drive booking, multi-city on-road pricing, user accounts.

## 12. Open questions for eng

1. Is the existing car DB already structured with all fields listed in §8, or do we need a data enrichment pass first?
2. Do we have on-road prices per city, or only ex-showroom?
3. LLM vendor & API key already provisioned?
