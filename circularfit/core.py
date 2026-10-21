"""CircularFit core logic: material catalogue, carbon estimate, matching, synthetic precinct data.

All data here is synthetic or an assumption. See the "Method & data" page in the app.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------------------------------------------------------- catalogue
# kg_per_unit and kgco2e_per_kg are assumptions. Rows marked "ICE v4" use values found in the
# ICE database v4 (cradle-to-gate, A1-A3, via Climatiq). Other rows are PLACEHOLDERS to verify.
CATALOGUE = pd.DataFrame(
    [
        # key, label, unit, kg/unit, kgCO2e/kg, source, icon
        ("ceramic_tile", "Ceramic floor tile (box)", "box", 20.0, 0.80, "ICE v4 (factor); box weight assumed", "🟫"),
        ("porcelain_tile", "Porcelain tile (box)", "box", 22.0, 0.76, "ICE v4 (factor); box weight assumed", "⬜"),
        ("sanitaryware", "Sink / basin / WC (ceramic)", "piece", 15.0, 1.93, "ICE v4 (factor); weight assumed", "🚽"),
        ("timber_door", "Timber door", "piece", 25.0, 0.70, "PLACEHOLDER - verify", "🚪"),
        ("cabinet", "Kitchen cabinet (wood-based)", "piece", 30.0, 0.90, "PLACEHOLDER - verify", "🗄️"),
        ("faucet", "Tap / faucet (brass)", "piece", 1.2, 3.00, "PLACEHOLDER - verify", "🚰"),
    ],
    columns=["key", "label", "unit", "kg_per_unit", "kgco2e_per_kg", "source", "icon"],
).set_index("key")

CONDITIONS = {"New / unused": 1.0, "Good (used)": 0.8, "Fair (minor wear)": 0.5}
POINTS_PER_KG_CO2E = 10  # assumed; rewards are set by the developer, not the JMB
REWARD_TIERS = [(100, "Clubhouse day pass"), (250, "Cafe voucher at the precinct"), (500, "Service-charge rebate (needs developer/JMB approval)")]

GUARDHOUSE = "Precinct guardhouse staging zone"

# --------------------------------------------------------------------------- waste routing
# Waste hierarchy: Reuse > Salvage > Recycle > Landfill. Credits and thresholds are ASSUMPTIONS.
ROUTE_CREDIT = {"Reuse": 1.0, "Salvage": 0.8, "Recycle": 0.15, "Landfill": 0.0}  # defaults, share of reuse carbon credit kept
ROUTE_ORDER = ["Reuse", "Salvage", "Recycle", "Landfill"]
STAGING_CAPACITY_KG = 500   # guardhouse staging zone (assumed)
RECYCLE_MIN_KG = 20         # smallest batch a recycler will collect (assumed)
SKIP_BIN_KG = 3000          # waste carried by one skip bin ("roro") load (assumed)
REUSABLE_SHARE = 0.32       # share of housing waste that could be reused or recycled (Malaysian estimate, Ain Shams Eng. J. 2021)
AVG_FACTOR = 1.0            # average kg CO2e per kg of renovation material (placeholder)
AVG_ROUTE_CREDIT = 0.7      # average route credit across a mix of routes (placeholder)


# Editable assumptions (admin Settings page). The app copies its session copy into CFG on every run.
DEFAULT_CFG = {
    "staging_capacity_kg": STAGING_CAPACITY_KG,
    "recycle_min_kg": RECYCLE_MIN_KG,
    "skip_bin_kg": SKIP_BIN_KG,
    "reusable_share": REUSABLE_SHARE,
    "avg_factor": AVG_FACTOR,
    "avg_route_credit": AVG_ROUTE_CREDIT,
    "points_per_kg": POINTS_PER_KG_CO2E,
    "credit_Reuse": ROUTE_CREDIT["Reuse"],
    "credit_Salvage": ROUTE_CREDIT["Salvage"],
    "credit_Recycle": ROUTE_CREDIT["Recycle"],
    "credit_Landfill": 0.0,
}
CFG = dict(DEFAULT_CFG)


def route_credit(route: str) -> float:
    return CFG[f"credit_{route}"]


def recommend_route(row, matched: bool, staging_free_kg: float) -> tuple[str, str]:
    """Pick the highest route in the waste hierarchy that is available for this item."""
    if matched:
        return "Reuse", "A neighbour within the radius has requested this material."
    if row.condition != "Fair (minor wear)" and staging_free_kg >= row.weight_kg:
        return "Salvage", "Good condition: stage at the guardhouse for the weekly salvage-partner pickup."
    if row.weight_kg >= CFG["recycle_min_kg"]:
        return "Recycle", "Not reusable right now: the batch is big enough for recycler collection."
    return "Landfill", "Small, worn batch below the recycler minimum: residual skip bin."


def forecast(homes: int, pct_renovating: float, kg_per_home: float, capture: float) -> dict:
    """Handover-wave waste forecast for a precinct (planning estimate, all inputs are assumptions)."""
    waste_kg = homes * pct_renovating * kg_per_home
    divertible_kg = waste_kg * CFG["reusable_share"]
    diverted_kg = divertible_kg * capture
    return {
        "waste_t": waste_kg / 1000,
        "divertible_t": divertible_kg / 1000,
        "diverted_t": diverted_kg / 1000,
        "bins_total": waste_kg / CFG["skip_bin_kg"],
        "bins_avoided": diverted_kg / CFG["skip_bin_kg"],
        "carbon_t": diverted_kg * CFG["avg_factor"] * CFG["avg_route_credit"] / 1000,
    }


def estimate(material: str, quantity: float, condition: str) -> dict:
    """Weight and embodied carbon avoided if the material is reused instead of dumped.

    carbon_saved = weight x factor x reuse_credit, where the credit is lower for worn items
    because they replace less new material. Counts production carbon (A1-A3) only.
    """
    row = CATALOGUE.loc[material]
    weight = row.kg_per_unit * quantity
    credit = CONDITIONS[condition]
    carbon = weight * row.kgco2e_per_kg * credit
    return {
        "weight_kg": round(weight, 1),
        "carbon_kg": round(carbon, 1),
        "points": int(round(carbon * CFG["points_per_kg"])),
    }


# --------------------------------------------------------------------------- precinct
GRID_COLS = 8
GRID_ROWS = 6
SPACING_M = 85  # distance between neighbouring houses in the demo layout (metres)


def build_houses() -> pd.DataFrame:
    rows = []
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            rows.append({"house": f"Lot {r * GRID_COLS + c + 1:02d}", "x": c * SPACING_M, "y": r * SPACING_M})
    return pd.DataFrame(rows)


def distance_m(houses: pd.DataFrame, a: str, b: str) -> float:
    ha = houses.loc[houses.house == a].iloc[0]
    hb = houses.loc[houses.house == b].iloc[0]
    return float(math.hypot(ha.x - hb.x, ha.y - hb.y))


# --------------------------------------------------------------------------- synthetic seed
def seed_data(houses: pd.DataFrame, n_listings: int = 14, n_requests: int = 10, rng_seed: int = 7):
    rng = random.Random(rng_seed)
    names = ["Irfan", "Daniel", "Mei Ling", "Raj", "Farah", "Hakim", "Siti", "Kumar", "Amir", "Jia Wen",
             "Nurul", "Faiz", "Priya", "Zul", "Hana", "Wei Jie"]
    lots = list(houses.house)
    notes = {
        "ceramic_tile": ["leftover wet-area floor tiles, developer standard", "spare tiles from kitchen floor", "unopened boxes of floor tiles"],
        "porcelain_tile": ["porcelain tiles, 600x600, surplus from bathroom", "matt porcelain tiles leftover"],
        "sanitaryware": ["removed kitchen sink, developer standard", "bathroom basin, never used", "white ceramic WC, removed during upgrade"],
        "timber_door": ["bedroom door removed for replacement", "solid timber door, good condition"],
        "cabinet": ["wall cabinet from old kitchen layout", "base cabinet, removed during renovation"],
        "faucet": ["kitchen tap, developer standard", "bathroom mixer tap, unused"],
    }
    listings = []
    for i in range(n_listings):
        m = rng.choice(list(CATALOGUE.index))
        qty = rng.choice([1, 2, 3, 4, 6]) if CATALOGUE.loc[m].unit == "box" else rng.choice([1, 1, 2])
        cond = rng.choice(list(CONDITIONS))
        e = estimate(m, qty, cond)
        listings.append({
            "id": f"L{i + 1:03d}", "owner": rng.choice(names), "house": rng.choice(lots), "material": m,
            "quantity": qty, "condition": cond, "note": rng.choice(notes[m]), "status": "open",
            "weight_kg": e["weight_kg"], "carbon_kg": e["carbon_kg"], "day": rng.randint(1, 20),
        })
    requests = []
    needs = {
        "ceramic_tile": ["need a few boxes of floor tiles to patch a cracked area", "tiles for garden stepping stones"],
        "porcelain_tile": ["porcelain tiles for a balcony patch"],
        "sanitaryware": ["spare sink for the car porch utility area"],
        "timber_door": ["door for a storeroom"],
        "cabinet": ["cabinet for garage storage"],
        "faucet": ["tap for the outdoor wash area"],
    }
    for i in range(n_requests):
        m = rng.choice(list(CATALOGUE.index))
        qty = rng.choice([1, 2, 3]) if CATALOGUE.loc[m].unit == "box" else 1
        requests.append({"id": f"R{i + 1:03d}", "owner": rng.choice(names), "house": rng.choice(lots),
                         "material": m, "quantity": qty, "note": rng.choice(needs[m]), "status": "open"})
    ledger = pd.DataFrame(columns=["id", "day", "material", "weight_kg", "carbon_kg", "donor", "receiver", "distance_m", "route"])
    # a few completed hand-offs so the dashboard is not empty on first load
    for i in range(6):
        m = rng.choice(list(CATALOGUE.index))
        qty = rng.choice([2, 3, 4]) if CATALOGUE.loc[m].unit == "box" else 1
        e = estimate(m, qty, "Good (used)")
        route = rng.choice(["Reuse", "Reuse", "Salvage", "Salvage", "Recycle"])
        reuse = route == "Reuse"
        partner = {"Salvage": "Salvage partner", "Recycle": "Recycler"}.get(route)
        ledger.loc[len(ledger)] = [f"H{i + 1:03d}", rng.randint(1, 18), m, e["weight_kg"],
                                   round(float(e["carbon_kg"]) * ROUTE_CREDIT[route], 1), rng.choice(names),
                                   rng.choice(names) if reuse else partner,
                                   rng.choice([85, 120, 170, 240, 300]) if reuse else 0, route]
    return pd.DataFrame(listings), pd.DataFrame(requests), ledger


# --------------------------------------------------------------------------- matching
@dataclass
class MatchWeights:
    material: float = 0.40
    text: float = 0.20
    proximity: float = 0.25
    quantity: float = 0.15


def match(listings: pd.DataFrame, requests: pd.DataFrame, houses: pd.DataFrame, radius_m: float,
          w: MatchWeights = MatchWeights()) -> pd.DataFrame:
    """Score every open listing/request pair of the same material.

    score = 0.40 material match + 0.20 text similarity (TF-IDF) + 0.25 proximity + 0.15 quantity cover.
    Pairs outside `radius_m` are dropped. One listing is assigned to at most one request.
    """
    L = listings[listings.status == "open"].reset_index(drop=True)
    R = requests[requests.status == "open"].reset_index(drop=True)
    if L.empty or R.empty:
        return pd.DataFrame()
    docs = list(L.note) + list(R.note)
    tf = TfidfVectorizer(stop_words="english").fit(docs)
    sim = cosine_similarity(tf.transform(L.note), tf.transform(R.note))
    rows = []
    for i, l in L.iterrows():
        for j, r in R.iterrows():
            if l.material != r.material or l.house == r.house or l.owner == r.owner:
                continue
            d = distance_m(houses, l.house, r.house)
            if d > radius_m:
                continue
            prox = 1 - d / radius_m
            qty = min(1.0, l.quantity / max(r.quantity, 1))
            score = w.material * 1 + w.text * float(sim[i, j]) + w.proximity * prox + w.quantity * qty
            rows.append({"listing": l.id, "request": r.id, "material": l.material, "donor": l.owner,
                         "receiver": r.owner, "donor_house": l.house, "receiver_house": r.house,
                         "distance_m": round(d), "score": round(100 * score), "weight_kg": l.weight_kg,
                         "carbon_kg": l.carbon_kg})
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).sort_values("score", ascending=False)
    df = df.drop_duplicates("listing").drop_duplicates("request").reset_index(drop=True)
    return df
