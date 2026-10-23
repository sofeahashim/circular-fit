# CircularFit

**CircularFit: Keeping Handover Renovation Waste Out of Skip Bins.** A Streamlit prototype for the Sime Darby Property University Hackathon 2026 (Planet track). It routes renovation waste from newly handed-over homes to a neighbour, a salvage partner or a recycler before landfill, and gives township management a dashboard of the tonnes, skip bins and carbon avoided.

The pitch deck is in [`pitch/`](pitch/CircularFit_Pitch%20Deck.pdf). All data in the app is synthetic.

## Run
```
pip install -r requirements.txt
python -m streamlit run app.py
```
Open http://localhost:8501.

## Roles (demo switch, no login)
**Resident** (Home, Log items, Find materials, Hand-offs, My impact) and **Township admin** (Overview, Routing, Planner, Settings). Both see About. Switch with the "View as" control at the top. Deep link: `/planner?role=admin`.

## Pages
- **Resident / Home:** what to do next, headline numbers and the five-step flow.
- **Log items:** pick a material, quantity and condition. See the likely route and impact before confirming.
- **Find materials:** neighbours' items within a walking radius, with a request dialog.
- **Hand-offs:** when an item is matched, the donor and the requester each agree or decline. A decline sends the item back to routing.
- **My impact:** green points, reward progress, my items and requests.
- **Admin / Overview:** tonnes, skip-bin loads and carbon avoided, route split, precinct map, leaderboard, CSV export.
- **Routing:** each item goes up the waste hierarchy: Reuse > Salvage (staging zone) > Recycle > Landfill. Confirm hand-offs (unlocked only after both residents agree, then a second confirmation pop-up) and run weekly collection.
- **Planner:** forecasts waste for a handover wave and how much can be diverted.
- **Settings:** edit every assumption (capacity, thresholds, carbon credits, points).
- **About:** method, assumptions and limits.

## Files
- `app.py`: navigation, roles and header
- `circularfit/core.py`: catalogue, carbon estimate, routing, forecast, matching, synthetic data, editable `CFG`
- `circularfit/state.py`: session state and ledger
- `circularfit/views.py`: all pages
- `circularfit/ui.py`: dark theme, components and GSAP motion
- `circularfit/charts.py`: themed Altair charts

## Design
Dark theme inspired by gsap.com (near-black, cream text, green gradient, pill buttons). Font: Hanken Grotesk (a free stand-in for Mori). Motion uses GSAP from cdnjs (needs internet; falls back to no animation).

## Data and assumptions
- All residents, listings and hand-offs are synthetic (fixed random seed).
- Emission factors are from the CIDB Malaysia inventory, *Embodied Carbon Inventory Data for Construction Materials* (2021, cradle-to-gate). Where it lists a range the lower value is used. The kg-per-unit weights are **assumptions** (the inventory gives none).
- Carbon avoided = weight x factor x condition credit x route credit (production stage only). Route credits, staging capacity, recycler minimum and skip-bin size are assumptions.
- Not built yet: a vision model to recognise materials from photos, real accounts, a live backend.
