# CircularFit: pitch deck draft

Sime Darby Property University Hackathon 2026 · Planet track · Township of Tomorrow
Submission: 10 main slides maximum, appendix allowed. Due 11:59 PM, 23 Oct 2026.

Anything marked **[TEAM TO FILL]** or **[VERIFY]** is not yet true or sourced. Do not present it as fact.

---

## How the deck follows the official template

| Template slide | Our slide |
|---|---|
| Team information | Slide 1 (shared with the cover) |
| 1. The Problem | Slide 2 |
| 2. Target User | Slide 3 |
| 3. Your Solution | Slide 4 |
| 4. Innovation | Slide 5 |
| 5. How it Works | Slide 6 |
| 6. Impact | Slide 7 |
| 7. Feasibility | Slide 8 |
| 7. Implementation | Slide 9 |
| 7. Visual Concept | Woven into slides 4 and 6, full set in Appendix A1 |
| 8. Why Your Team Should Win (100 words max) | Slide 10 |
| Thank you | Last line of slide 10 |

The template has 11 content slides. To stay within 10, we merge the cover with team info and move the visual concept into the solution slides and the appendix.

## How each slide supports the judging criteria

| Criterion (weight) | Slides |
|---|---|
| Impact & sustainability value (25%) | 2, 7 |
| Innovation & differentiation (20%) | 5 |
| Feasibility & deliverability (20%) | 8, 9 |
| Strategic fit & theme relevance (15%) | 2, 3, 9 |
| Commercial & value multiplication (10%) | 7, 9 |
| Team, evidence & pitch quality (10%) | 1, 10, all evidence labels |

One problem runs through every slide, as the template advises: **handover renovation waste going into skip bins.**

---

## Main deck

### Slide 1. Cover and team
**Message:** CircularFit keeps handover renovation waste out of skip bins.
- Title: **CircularFit**
- Tagline: *Don't skip it. Share it.*
- Track: Planet (Circular Economy & Waste Management)
- Team table: team name, leader, university, members (3 to 5), email, contact number. **[TEAM TO FILL]**
- Course context: ISP624 Special Topics in Artificial Intelligence. **[TEAM TO FILL if you want it shown]**
- Visual: brand mark and the green gradient from the app.

### Slide 2. The problem
**Message:** Every handover triggers a renovation rush, and the strip-out goes into skip bins.
- Scenario: hundreds of homes are handed over in a new precinct. Owners and contractors strip out fixtures and discard leftover tiles, sinks, doors and cabinets, often brand new.
- Why it matters:
  - Housing-sector waste is estimated at about 16% of materials used, around 8.8 million tonnes a year, and about 32% of it could be reused or recycled (*Ain Shams Engineering Journal*, 2021).
  - Malaysia faces a shortage of landfill space (UTHM study, construction and demolition waste).
  - Dumped materials carry embodied carbon that is thrown away with them.
- Evidence gap: we have no source yet that says "most owners renovate right after handover". **[VERIFY: 3 to 5 quick interviews with new homeowners or renovation contractors, or soften to "many owners".]**
- Visual: a skip bin full of intact tiles and a sink (stock or AI image), with the stats beside it.

### Slide 3. Target users
**Message:** Three groups, one shared problem.
- **Residents and contractors (donors):** want a quick, free way to get rid of strip-out items without ordering extra skip bins.
- **Neighbours (requesters):** need a few tiles for a patch, a door for a storeroom, a sink for the car porch.
- **Township management (admin, the customer):** needs to cut waste, report sustainability numbers and plan for the next handover wave.
- Supporting partners: salvage partner, recycler, guardhouse staff.
- Visual: three persona cards, each with one pain point and one thing CircularFit gives them.

### Slide 4. The solution
**Message:** Log it, route it, prove it.
- CircularFit routes each item to the best available option: **Reuse** with a neighbour, **Salvage** via the guardhouse staging zone, **Recycle**, and **Landfill** only as a last resort.
- For residents: log items in about a minute, see the likely route and impact first, earn green points.
- For township management: a routing console, a handover planner and an auditable ledger.
- Visual: three prototype screenshots (Log items, Hand-offs, Admin overview). Use real screens from the app.

### Slide 5. Innovation
**Message:** Not another marketplace: a waste-routing system built on the handover moment.
- Waste-hierarchy routing: reuse before salvage before recycling before landfill, decided per item.
- Hyper-local: matching within a few hundred metres, with a staging zone at the guardhouse.
- Handover-wave planner: forecasts waste for a precinct so the developer can size staging and book pickups.
- Two-sided agreement plus admin confirmation: only real hand-offs count, which keeps the numbers auditable.
- Per-item carbon estimate from a materials catalogue.
- Comparison: existing leftover-material platforms (such as Enviromate in the UK) let tradespeople list and trade surplus materials locally. They do not route waste across reuse, salvage and recycling, or report to a developer. **[VERIFY competitor claims before showing them.]**
- Visual: comparison table.

### Slide 6. How it works
**Message:** From strip-out to ledger in six steps.
1. **Log:** material, quantity, condition, optional photo.
2. **Estimate:** weight and carbon saved from the catalogue.
3. **Route:** the first route that applies wins (Reuse, Salvage, Recycle, Landfill).
4. **Agree:** donor and requester each say yes or no on their Hand-offs page.
5. **Confirm:** the admin confirms once both agree, after a second confirmation pop-up.
6. **Report:** the ledger feeds the dashboard and resident points.
- Matching score (for reuse): 40% material + 20% text similarity + 25% proximity + 15% quantity cover. It is a ranking aid, not the final decision.
- Visual: the flow diagram, with the four routes shown as coloured chips. Roles shown in the legend (Resident, Township admin).

### Slide 7. Impact
**Message:** One handover wave can divert tens of tonnes (planning scenario).
- Scenario, all inputs are assumptions: 300 homes, 60% renovating, 900 kg of waste per renovating home, 30% of divertible waste captured.
- Result from the Handover Planner: about **162 tonnes** of renovation waste, about **52 tonnes** divertible, about **15.6 tonnes** diverted, about **5.2 of 54** skip-bin loads avoided, about **10.9 t CO₂e** avoided.
- Who benefits:
  - Township management: lower disposal volume, auditable ESG numbers.
  - Residents: free materials, green points.
  - Environment: less landfill, less new material produced.
- Value multiplication (hypotheses to test in a pilot): fewer skip-bin hauls, reporting for sustainability disclosures, resident engagement, and a model any township can copy. **[VERIFY with the developer or a mentor.]**
- Label clearly: "Planning scenario. Replace waste per home with precinct data."
- Visual: the planner chart from the app and three big numbers.

### Slide 8. Feasibility
**Message:** Built on proven parts, and it already runs.
- Working prototype: Streamlit and Python web app with synthetic data, covering the full loop (log, route, agree, confirm, report).
- Needs no proprietary data: carbon factors come from public databases (ICE database v4 for tile and sanitaryware), and the rest are labelled assumptions.
- What it needs on the ground: a staging area at the guardhouse, a salvage partner, a recycler, and agreement from the Joint Management Body (JMB).
- Risks and mitigations:
  - Low adoption: start at handover, when renovation is highest, and add rewards.
  - Contractors prefer skip bins: add a quick batch-listing flow.
  - Safety and liability of used fixtures: condition check and no-warranty notice.
  - Small batches not worth collecting: recycler minimum batch size and a staging zone.
- Visual: a risks-and-mitigation table.

### Slide 9. Implementation
**Message:** Pilot one handover wave, measure, then scale.
- **Phase 0 (weeks 0 to 4):** agree the pilot precinct, staging space and partners; set a baseline of waste per home.
- **Phase 1 (weeks 5 to 16):** run one handover wave with resident and admin roles; track diverted tonnes, skip-bin loads avoided and carbon avoided.
- **Phase 2:** extend across the township; add real sign-in verified against handover records, reminders and a QR check-in at the guardhouse.
- **Phase 3:** offer to other developers and townships across Malaysia.
- Who does what: developer (sponsor, staging zone), JMB (resident access), partners (collection), admin (daily operation).
- Timeline is a proposal. **[TEAM TO ADJUST]**
- Visual: a simple four-phase timeline.

### Slide 10. Why our team should win
**Message:** A measurable circular programme, not another marketplace. (85 words, within the 100-word limit)
> CircularFit turns the handover renovation rush into a measurable circular-economy programme. Instead of another marketplace, it routes every strip-out item up the waste hierarchy, to a neighbour, a salvage partner or a recycler, before landfill. Residents log and agree in minutes. Township management gets a handover planner, a routing console and an auditable ledger of tonnes, skip bins and carbon avoided. It is built on Sime Darby Property's own handover moment, scales to any Malaysian township, and our working prototype already runs the full loop.

Close with: **Thank you** · team name and contact. **[TEAM TO FILL]**

---

## Appendix (allowed, not counted in the 10)

- **A1. Prototype screens (visual concept):** resident home, log items, hand-offs, admin overview, routing, planner.
- **A2. Carbon method and assumptions:** `carbon avoided = weight × emission factor × condition credit × route credit`, with the materials catalogue. Mark placeholders. Production stage only; transport and end-of-life are ignored.
- **A3. Routing and matching rules:** thresholds (staging capacity, recycler minimum, skip-bin size) and the match score formula.
- **A4. Roles and the hand-off agreement flow:** resident, township admin, partners, guardhouse staff.
- **A5. Data sources and limitations:** all data is synthetic; no vision model yet; demo sign-in only; sources listed.
- **A6. Competitive landscape:** detail behind slide 5. **[VERIFY]**

---

## Open items before we design

1. **[TEAM TO FILL]** team name, leader, university, member details, contacts.
2. **[VERIFY]** evidence that many owners renovate soon after handover.
3. **[VERIFY]** claims about leftover-material platforms such as Enviromate.
4. Replace placeholder carbon factors (doors, cabinets, taps) and the assumed weights with cited values, or label them clearly as assumptions.
5. Take clean screenshots of the app for slides 4 and 6 and Appendix A1.
6. Decide the pilot numbers on slide 9 (precinct size, duration).
