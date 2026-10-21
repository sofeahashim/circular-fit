"""CircularFit: renovation waste diversion for new-home precincts (Streamlit prototype)."""
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="CircularFit", page_icon="♻️", layout="wide", initial_sidebar_state="collapsed")

from circularfit import state, ui, views  # noqa: E402  (after set_page_config)

ui.inject()
state.init()
S = st.session_state

P = {
    "home": st.Page(views.home_resident, title="Home", icon=":material/home:", url_path="home", default=True),
    "log": st.Page(views.log_items, title="Log items", icon=":material/add_circle:", url_path="log"),
    "find": st.Page(views.find_items, title="Find materials", icon=":material/search:", url_path="find"),
    "handoffs": st.Page(views.handoffs, title="Hand-offs", icon=":material/handshake:", url_path="handoffs"),
    "impact": st.Page(views.my_impact, title="My impact", icon=":material/workspace_premium:", url_path="impact"),
    "overview": st.Page(views.overview, title="Overview", icon=":material/dashboard:", url_path="overview"),
    "routing": st.Page(views.routing, title="Routing", icon=":material/alt_route:", url_path="routing"),
    "planner": st.Page(views.planner, title="Planner", icon=":material/query_stats:", url_path="planner"),
    "settings": st.Page(views.settings, title="Settings", icon=":material/tune:", url_path="settings"),
    "method": st.Page(views.method, title="About", icon=":material/menu_book:", url_path="about"),
}
views.NAV.update(P)

if not S.get("role_ready"):
    S.role = "Township admin" if st.query_params.get("role") == "admin" else "Resident"
    S.role_ready = True
if S.get("role") not in ("Resident", "Township admin"):
    S.role = "Resident"
pages = ([P["home"], P["log"], P["find"], P["handoffs"], P["impact"], P["method"]] if S.role == "Resident"
         else [P["overview"], P["routing"], P["planner"], P["settings"], P["method"]])
nav = st.navigation(pages, position="top")

# ---- header: brand, role switch, profile
brand, role_col, who = st.columns([2.2, 3, 2.4], vertical_alignment="center")
brand.html(ui.brand())
role_col.segmented_control("View as", ["Resident", "Township admin"], key="role", label_visibility="collapsed")
st.query_params["role"] = "admin" if S.role == "Township admin" else "resident"
with who:
    if S.role == "Resident":
        with st.popover(f"👤 {S.me_name} · {S.me_house}", width="stretch"):
            names = sorted(set(S.listings.owner) | set(S.requests.owner) | {"Nadia", S.me_name})
            st.selectbox("Your name (demo)", names, key="me_name")
            S.me_house = st.selectbox("Your home", list(S.houses.house), index=list(S.houses.house).index(S.me_house))
            st.caption("Demo only: no login. Everyone and all listings are made up.")
    else:
        st.html('<div style="text-align:right"><span class="cf-chip" style="--c:#9d95ff"><i></i>Township admin · demo</span></div>')

nav.run()
