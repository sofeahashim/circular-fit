# CircularFit

Hyper-local salvage network for renovation materials (Sime Darby Property University Hackathon 2026, Planet track). Streamlit prototype.

## Run
```
pip install -r requirements.txt
python -m streamlit run app.py
```
Open http://localhost:8501.

## Roles (demo switch, no login)
**Resident** (Home, Log items, Find materials, My impact) and **Township admin** (Overview, Routing, Planner, Settings). Both see About. Switch with the "View as" control at the top. Deep link: `/planner?role=admin`.

## Pages
- **Resident / Home:** what to do next, headline numbers and the five-step flow.
- **Log items:** pick a material, quantity and condition. See the likely route and impact before confirming.
- **Find materials:** neighbours' items within a walking radius, with a request dialog.
- **My impact:** green points, reward progress, my items and requests.
- **Admin / Overview:** tonnes, skip-bin loads and carbon avoided, route split, precinct map, leaderboard, CSV export.
- **Routing:** each item goes up the waste hierarchy: Reuse > Salvage (staging zone) > Recycle > Landfill. Confirm hand-offs and run weekly collection.
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
- Tile and sanitaryware emission factors are from the ICE database v4 (cradle-to-gate). Other factors and all kg-per-unit weights are **placeholders to verify** before submission.
- Carbon avoided = weight x factor x condition credit x route credit (production stage only). Route credits, staging capacity, recycler minimum and skip-bin size are assumptions.
- Not built yet: a vision model to recognise materials from photos, real accounts, a live backend.
