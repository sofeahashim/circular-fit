"""Session state and ledger helpers for CircularFit."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from . import core
from .core import CFG, DEFAULT_CFG, build_houses, route_credit, seed_data

PARTNER_NAMES = ["Salvage partner", "Recycler"]


def init() -> None:
    """Create the session state once and push the session's assumptions into core.CFG."""
    S = st.session_state
    if "houses" not in S:
        houses = build_houses()
        listings, requests, ledger = seed_data(houses)
        ledger["donor_pts"] = (ledger.carbon_kg * DEFAULT_CFG["points_per_kg"]).round().astype(int)
        ledger["receiver_pts"] = (ledger.carbon_kg * DEFAULT_CFG["points_per_kg"] * 0.5).round().astype(int)
        ledger.loc[ledger.route != "Reuse", "receiver_pts"] = 0
        S.update(houses=houses, listings=listings, requests=requests, ledger=ledger,
                 next_listing=len(listings) + 1, next_request=len(requests) + 1, day=21,
                 cfg=dict(DEFAULT_CFG), role="Resident", me_name="Nadia", me_house="Lot 12")
    CFG.update(S.cfg)


def staging_used() -> float:
    return float(st.session_state.listings.loc[st.session_state.listings.status == "staged", "weight_kg"].sum())


def log_diversion(listing, route: str, receiver: str, distance: float = 0) -> None:
    """Close a listing and record the diversion in the ledger."""
    S = st.session_state
    carbon = round(float(listing.carbon_kg) * route_credit(route), 1)
    donor_pts = int(round(carbon * CFG["points_per_kg"]))
    row = {"id": f"H{len(S.ledger) + 1:03d}", "day": S.day, "material": listing.material,
           "weight_kg": listing.weight_kg, "carbon_kg": carbon, "donor": listing.owner, "receiver": receiver,
           "distance_m": distance, "route": route, "donor_pts": donor_pts,
           "receiver_pts": int(round(donor_pts * 0.5)) if route == "Reuse" else 0}
    S.ledger = pd.concat([S.ledger, pd.DataFrame([row])], ignore_index=True)
    S.listings.loc[S.listings.id == listing.id, "status"] = "done"


def points_for(name: str) -> int:
    led = st.session_state.ledger
    return int(led.loc[led.donor == name, "donor_pts"].sum() + led.loc[led.receiver == name, "receiver_pts"].sum())
