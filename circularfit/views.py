"""Pages for the Resident and Township admin roles."""
from __future__ import annotations

from types import SimpleNamespace

import pandas as pd
import streamlit as st

from . import charts, ui
from .core import (CATALOGUE, CFG, CONDITIONS, DEFAULT_CFG, GUARDHOUSE, REWARD_TIERS, ROUTE_ORDER, distance_m, estimate,
                   forecast, match, recommend_route, route_credit)
from .state import PARTNER_NAMES, agreement, both_agreed, log_diversion, points_for, staging_used
from .ui import BLUE, GREEN, LILAC, LIME, ORANGE, PINK, ROUTE_COLOR

S = st.session_state
NAV: dict = {}  # filled by app.py with st.Page objects so pages can link to each other
LABEL = CATALOGUE["label"].to_dict()
ICON = CATALOGUE["icon"].to_dict()


def fmt_mat(k: str) -> str:
    return f"{ICON[k]} {LABEL[k]}"


def _go(key: str, label: str, **kw) -> None:
    if key in NAV:
        st.page_link(NAV[key], label=label, **kw)


def _card_title(text: str, sub: str = "") -> None:
    st.html(f'<div style="margin:.1rem 0 .6rem"><div style="font-size:1.2rem;font-weight:700;letter-spacing:-.02em">{ui.esc(text)}</div>'
            + (f'<div style="color:var(--muted);font-size:.9rem">{ui.esc(sub)}</div>' if sub else "") + "</div>")


# =============================================================== RESIDENT
def home_resident() -> None:
    ui.hero("For residents and contractors",
            ["Keep handover", "waste out of", "the <em>skip bin.</em>"],
            "Renovating a new home? Log what you strip out or have left over. CircularFit finds the best place for it: "
            "a neighbour, a salvage partner or a recycler, and only then landfill.")
    led = S.ledger
    ui.kpis([("Items diverted so far", len(led), "items", 0, GREEN),
             ("Waste kept out of skip bins", round(float(led.weight_kg.sum())), "kg", 0, LIME),
             ("Carbon avoided (estimate)", round(float(led.carbon_kg.sum())), "kg CO₂e", 0, BLUE)])
    st.html('<div class="cf-head"><div class="cf-eyebrow">Start here</div><h1>What do you want to do?</h1></div>')
    c = st.columns(3)
    cards = [("01", "Log leftovers", "Tiles, sinks, doors, cabinets. Takes about a minute.", GREEN, "log", "Log items"),
             ("02", "Find materials", "See what neighbours within a few hundred metres are sharing.", BLUE, "find", "Browse nearby"),
             ("03", "See my impact", "Your green points, rewards and the items you have logged.", LILAC, "impact", "My impact")]
    for col, (n, t, d, acc, key, label) in zip(c, cards):
        with col:
            st.html(ui.action_card(n, t, d, acc))
            _go(key, f"{label} →")
    st.html('<div class="cf-head" style="margin-top:2.2rem"><div class="cf-eyebrow">How it works</div><h1>From skip bin to second life</h1></div>')
    ui.flow()


def log_items() -> None:
    ui.page_head("Resident", "Log your leftovers",
                 "Tell us what you have. We estimate the impact and show where it would go before you confirm.")
    left, right = st.columns([3, 2], gap="large")
    with left:
        with st.container(border=True):
            _card_title("1. What do you have?")
            mat = st.selectbox("Material", list(CATALOGUE.index), format_func=fmt_mat, label_visibility="collapsed")
            unit = CATALOGUE.loc[mat, "unit"]
            a, b = st.columns(2)
            qty = a.number_input(f"How many ({unit}s)?", 1, 50, 4 if unit == "box" else 1)
            cond = b.selectbox("Condition", list(CONDITIONS))
            _card_title("2. Add details", "Optional. A photo and a note help neighbours.")
            photo = st.file_uploader("Photo", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
            if photo:
                st.image(photo, width=260)
            default_note = f"{qty} {unit}{'s' if qty > 1 else ''} of {LABEL[mat].lower()}"
            note = st.text_input("Description", placeholder=default_note)
    est = estimate(mat, qty, cond)
    pseudo = SimpleNamespace(condition=cond, weight_kg=est["weight_kg"])
    wants = S.requests[(S.requests.status == "open") & (S.requests.material == mat) & (S.requests.owner != S.me_name)]
    reuse = any(distance_m(S.houses, S.me_house, h) <= 400 for h in wants.house)
    route, why = recommend_route(pseudo, reuse, CFG["staging_capacity_kg"] - staging_used())
    with right:
        with st.container(border=True):
            _card_title("3. What happens next")
            st.html(f'<div style="margin:.2rem 0 1rem"><span class="cf-chip" style="--c:{ROUTE_COLOR[route]}"><i></i>Likely route: {route}</span>'
                    f'<div style="color:var(--muted);font-size:.9rem;margin-top:8px">{ui.esc(why)}</div></div>')
            ui.kpis([("Kept out of the skip bin", est["weight_kg"], "kg", 1, GREEN),
                     ("Carbon avoided if reused", est["carbon_kg"], "kg CO₂e", 1, BLUE),
                     ("Green points you earn", est["points"], "pts", 0, LILAC)])
            if st.button("Log this item", type="primary", width="stretch"):
                i = S.next_listing
                S.listings = pd.concat([S.listings, pd.DataFrame([{
                    "id": f"L{i:03d}", "owner": S.me_name, "house": S.me_house, "material": mat, "quantity": qty,
                    "condition": cond, "note": note.strip() or default_note, "status": "open",
                    "weight_kg": est["weight_kg"], "carbon_kg": est["carbon_kg"], "day": S.day}])], ignore_index=True)
                S.next_listing += 1
                st.toast(f"Logged {default_note}.", icon="✅")
                S.logged = True
    if S.pop("logged", False):
        st.success("Item logged. It now appears for your township admin to route, and neighbours can request it.")
        _go("impact", "See my items →")


@st.dialog("Request this item")
def _request_dialog(row) -> None:
    st.markdown(f"**{fmt_mat(row.material)}** from {row.owner} ({row.house})")
    avail = max(1, int(row.quantity))
    st.caption(f"{avail} available. You can request up to {avail}.")
    need = st.number_input("How many do you need?", 1, avail, 1)
    why = st.text_input("What will you use it for?", placeholder="e.g. patching cracked kitchen floor tiles")
    if st.button("Send request", type="primary", disabled=not why.strip()):
        r = S.next_request
        S.requests = pd.concat([S.requests, pd.DataFrame([{
            "id": f"R{r:03d}", "owner": S.me_name, "house": S.me_house, "material": row.material,
            "quantity": need, "note": why.strip(), "status": "open"}])], ignore_index=True)
        S.next_request += 1
        st.toast("Request sent.", icon="📨")
        st.rerun()


def find_items() -> None:
    ui.page_head("Resident", "Find materials nearby",
                 f"Items shared by neighbours close to {S.me_house}. Request what you need before it is routed elsewhere.")
    with st.container(border=True):
        a, b = st.columns([2, 3], gap="large")
        radius = a.slider("How far will you walk? (metres)", 100, 600, 400, step=50)
        mats = b.pills("Material", list(CATALOGUE.index), selection_mode="multi", format_func=fmt_mat)
    L = S.listings[S.listings.status == "open"].copy()
    L["distance_m"] = [round(distance_m(S.houses, S.me_house, h)) for h in L.house]
    L = L[(L.distance_m <= radius) & (L.owner != S.me_name)]
    if mats:
        L = L[L.material.isin(mats)]
    L = L.sort_values("distance_m")
    st.html(f'<div style="margin:1rem 0 .4rem;color:var(--muted);font-weight:600">{len(L)} item{"s" if len(L) != 1 else ""} within {radius} m</div>')
    if L.empty:
        st.info("Nothing within this distance yet. Try a bigger radius.")
    for _, row in L.iterrows():
        c1, c2 = st.columns([6, 1.4], vertical_alignment="center")
        c1.html(ui.item_card(ICON[row.material], f"{LABEL[row.material]} × {row.quantity}", f"{row.note}",
                             f"{row.distance_m} m", f"{row.carbon_kg:.0f} kg CO₂e saved",
                             ui.chip(row.condition, LIME) + " " + ui.chip(f"{row.owner} · {row.house}", BLUE)))
        if c2.button("Request", key=f"rq_{row.id}", width="stretch"):
            _request_dialog(row)


# --------------------------------------------------------------- resident hand-offs
def _agree(listing_id: str, request_id: str, role: str) -> None:
    agreement(listing_id, request_id)[role] = "agreed"
    st.toast("You agreed. The other side has been notified.", icon="✅")


def _act_as(name: str) -> None:
    S.me_name = name
    S.me_name_pick = name  # keep the profile menu in step


@st.dialog("Decline this hand-off?")
def _decline_dialog(m, role: str) -> None:
    st.markdown("The item goes back to routing and the other resident is told. You can still be matched with someone else.")
    st.selectbox("Reason", ["Changed my mind", "Item no longer available", "Too far to collect", "Other"])
    a, b = st.columns(2)
    if a.button("Keep it", width="stretch"):
        st.rerun()
    if b.button("Yes, decline", type="primary", width="stretch"):
        S.blocked.add((m.listing, m.request))
        S.agree.pop(f"{m.listing}|{m.request}", None)
        st.toast("Declined. The item goes back to routing.", icon="↩️")
        st.rerun()


def handoffs() -> None:
    ui.page_head("Resident", "My hand-offs",
                 "When we match an item with a neighbour, you both say yes or no here. The township admin confirms once you both agree.")
    M = match(S.listings, S.requests, S.houses, 400, blocked=S.blocked)
    mine = [m for _, m in M.iterrows() if S.me_name in (m.donor, m.receiver)] if not M.empty else []
    if not mine:
        st.info(f"No proposed hand-offs for {S.me_name} right now. Log an item or request one and check back.")
        people = sorted({p for _, m in M.iterrows() for p in (m.donor, m.receiver)}) if not M.empty else []
        if people:
            _card_title("Demo: act as someone who has a proposed hand-off")
            cols = st.columns(min(len(people), 4))
            for i, p in enumerate(people):
                cols[i % len(cols)].button(f"Act as {p}", key=f"act_{p}", on_click=_act_as, args=(p,), width="stretch")
        return
    tone = {"agreed": ("agreed", GREEN), "pending": ("pending", ORANGE)}
    for m in mine:
        role = "donor" if m.donor == S.me_name else "requester"
        other_role = "requester" if role == "donor" else "donor"
        other = m.receiver if role == "donor" else m.donor
        other_house = m.receiver_house if role == "donor" else m.donor_house
        ag = agreement(m.listing, m.request)
        lst = S.listings[S.listings.id == m.listing].iloc[0]
        chips = (ui.chip(f"You ({role}): {tone[ag[role]][0]}", tone[ag[role]][1]) + " "
                 + ui.chip(f"{other} ({other_role}): {tone[ag[other_role]][0]}", tone[ag[other_role]][1]) + " "
                 + ui.chip(f"{m.distance_m} m apart", BLUE))
        st.html(ui.item_card(ICON[m.material], f"{LABEL[m.material]} × {lst.quantity}",
                             f"You are the {role}. The {other_role} is {other} ({other_house}).",
                             f"{m.weight_kg:.0f} kg", f"{m.carbon_kg:.0f} kg CO₂e", chips))
        if ag[role] == "pending":
            st.caption(f"Pickup: porch-to-porch, or at the {GUARDHOUSE.lower()}. Do you agree to this hand-off?")
            a, b, _ = st.columns([1.3, 1.3, 4])
            a.button("Agree", key=f"ag_{m.listing}", type="primary", on_click=_agree, args=(m.listing, m.request, role), width="stretch")
            if b.button("Decline", key=f"dc_{m.listing}", width="stretch"):
                _decline_dialog(m, role)
        elif both_agreed(m.listing, m.request):
            st.success("Both of you agreed. Meet at the porch or the staging zone. The township admin will confirm once it is done.")
        else:
            st.info(f"You agreed. Waiting for {other} to answer.")
        st.html('<div style="height:10px"></div>')


def my_impact() -> None:
    ui.page_head("Resident", "My impact", f"Everything {S.me_name} has logged, requested and earned.")
    pts = points_for(S.me_name)
    tiers = sorted(REWARD_TIERS)
    nxt = next((t for t in tiers if t[0] > pts), None)
    a, b = st.columns([2, 3], gap="large")
    with a:
        with st.container(border=True):
            st.html(f'<div class="cf-eyebrow">Green points</div><div class="cf-pts" style="margin:.6rem 0"><span class="cf-count" data-to="{pts}" data-dec="0">0</span></div>')
            if nxt:
                ui.meter(f"Next reward: {nxt[1]}", pts, nxt[0], f"{nxt[0] - pts} pts to go")
            else:
                st.success("You have unlocked every reward tier.")
            for need, name in tiers:
                st.html(f'<div style="display:flex;justify-content:space-between;padding:6px 0;border-top:1px solid var(--line);'
                        f'opacity:{1 if pts >= need else .55}"><span>{ui.esc(name)}</span><b>{need} pts</b></div>')
            ui.note("Rewards are assumptions. A service-charge rebate would need developer or JMB approval.")
    with b:
        mine = S.listings[S.listings.owner == S.me_name]
        _card_title("My items", "Logged by you")
        if mine.empty:
            st.info("You have not logged anything yet.")
            _go("log", "Log your first item →")
        status = {"open": ("Waiting to be routed", ORANGE), "staged": ("At the staging zone", BLUE), "done": ("Diverted", GREEN)}
        for _, row in mine.iterrows():
            lab, col = status[row.status]
            st.html(ui.item_card(ICON[row.material], f"{LABEL[row.material]} × {row.quantity}", row.note,
                                 f"{row.weight_kg:.0f} kg", f"{row.carbon_kg:.0f} kg CO₂e", ui.chip(lab, col)))
        reqs = S.requests[S.requests.owner == S.me_name]
        if not reqs.empty:
            _card_title("My requests")
            for _, row in reqs.iterrows():
                st.html(ui.item_card(ICON[row.material], f"{LABEL[row.material]} × {row.quantity}", row.note, "",
                                     "", ui.chip("Done" if row.status == "done" else "Open", GREEN if row.status == "done" else ORANGE)))


# =============================================================== ADMIN
def overview() -> None:
    ui.page_head("Township admin", "Overview",
                 "What the township has diverted from skip bins so far. All data in this prototype is synthetic.")
    led = S.ledger
    ui.kpis([("Waste diverted", round(led.weight_kg.sum() / 1000, 2), "tonnes", 2, GREEN),
             ("Skip-bin loads avoided", round(led.weight_kg.sum() / CFG["skip_bin_kg"], 2), "loads", 2, LIME),
             ("Carbon avoided", round(led.carbon_kg.sum() / 1000, 2), "t CO₂e", 2, BLUE),
             ("Items diverted", len(led), "items", 0, LILAC)])
    a, b = st.columns(2, gap="medium")
    with a:
        with st.container(border=True):
            _card_title("Where the waste went", "Share of diverted weight by route")
            st.altair_chart(charts.donut_routes(led), width="stretch", theme=None)
    with b:
        with st.container(border=True):
            _card_title("Cumulative waste diverted", "Over the handover month")
            st.altair_chart(charts.area_cumulative(led), width="stretch", theme=None)
    a, b = st.columns(2, gap="medium")
    with a:
        with st.container(border=True):
            _card_title("Carbon avoided by material", "kg CO₂e")
            st.altair_chart(charts.bars_carbon(led, LABEL), width="stretch", theme=None)
    with b:
        with st.container(border=True):
            _card_title("Precinct map", "Where waste and demand sit right now")
            st.altair_chart(charts.precinct_map(S.houses, S.listings, S.requests, S.me_house), width="stretch", theme=None)
    a, b = st.columns([3, 2], gap="medium")
    with a:
        with st.container(border=True):
            _card_title("Green points leaderboard")
            pts = pd.concat([led[["donor", "donor_pts"]].set_axis(["Resident", "Points"], axis=1),
                             led[["receiver", "receiver_pts"]].set_axis(["Resident", "Points"], axis=1)])
            pts = pts[~pts.Resident.isin(PARTNER_NAMES)]
            board = pts.groupby("Resident", as_index=False).Points.sum().sort_values("Points", ascending=False).head(6)
            st.altair_chart(charts.points_bars(board, 220), width="stretch", theme=None)
    with b:
        with st.container(border=True):
            _card_title("Export", "The full ledger as a spreadsheet")
            st.download_button("Download ledger (CSV)", led.to_csv(index=False), "circularfit_ledger.csv", "text/csv", width="stretch")
            ui.note("Synthetic data. Replace with real hand-off records in a live pilot.")


@st.dialog("Confirm this hand-off?")
def _confirm_handoff(row, m) -> None:
    carbon = round(float(row.carbon_kg) * route_credit("Reuse"), 1)
    pts = int(round(carbon * CFG["points_per_kg"]))
    st.html(f'''<div style="display:grid;gap:10px;margin-bottom:.4rem">
      <div class="cf-item" style="grid-template-columns:54px 1fr;margin:0"><div class="ic">{ICON[row.material]}</div>
        <div><b>{ui.esc(LABEL[row.material])} × {row.quantity}</b><span class="m">{row.weight_kg:.0f} kg · {ui.esc(row.condition)}</span></div></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div class="cf-card"><div class="cf-eyebrow">Donor</div><h3 style="margin-top:6px">{ui.esc(row.owner)}</h3><p>{ui.esc(row.house)}</p></div>
        <div class="cf-card"><div class="cf-eyebrow" style="color:var(--blue)">Requester</div><h3 style="margin-top:6px">{ui.esc(m.receiver)}</h3><p>{ui.esc(m.receiver_house)} · {m.distance_m} m away</p></div>
      </div></div>''')
    st.markdown(f"Recording this adds **{row.weight_kg:.0f} kg** diverted and **{carbon:.1f} kg CO₂e** avoided to the ledger, "
                f"and awards **{pts} points** to the donor and **{pts // 2}** to the requester. It cannot be undone in this prototype.")
    done = st.checkbox("The item has been handed over to the requester")
    a, b = st.columns(2)
    if a.button("Cancel", width="stretch"):
        st.rerun()
    if b.button("Yes, confirm hand-off", type="primary", disabled=not done, width="stretch"):
        S.requests.loc[S.requests.id == m.request, "status"] = "done"
        log_diversion(row, "Reuse", m.receiver, m.distance_m)
        st.toast("Hand-off recorded.", icon="🤝")
        st.rerun()


def routing() -> None:
    ui.page_head("Township admin", "Waste routing",
                 "Every logged item takes the best route available: reuse, then salvage, then recycle. Landfill is the last resort.")
    radius = st.slider("Reuse radius (metres)", 100, 600, 400, step=50)
    M = match(S.listings, S.requests, S.houses, radius, blocked=S.blocked)
    matched = {m.listing: m for _, m in M.iterrows()} if not M.empty else {}
    open_l = S.listings[S.listings.status == "open"].copy()
    free = CFG["staging_capacity_kg"] - staging_used()
    routes, reasons = [], []
    for _, row in open_l.iterrows():
        r, why = recommend_route(row, row.id in matched, free)
        if r == "Salvage":
            free -= row.weight_kg
        routes.append(r)
        reasons.append(why)
    open_l["route"], open_l["why"] = routes, reasons
    counts = open_l.groupby("route").agg(items=("id", "count"), kg=("weight_kg", "sum")).reindex(ROUTE_ORDER).fillna(0)
    ui.kpis([(f"{r} · {counts.loc[r, 'kg']:.0f} kg", int(counts.loc[r, "items"]), "items", 0, ROUTE_COLOR[r]) for r in ROUTE_ORDER])
    used = staging_used()
    ui.meter(f"Staging zone · {GUARDHOUSE.lower()}", used, CFG["staging_capacity_kg"], f"{used:.0f} / {CFG['staging_capacity_kg']:.0f} kg")

    tabs = st.tabs([f"{r} ({int(counts.loc[r, 'items'])})" for r in ROUTE_ORDER] + ["At staging zone"])

    def card(row, extra="", chips=""):
        return ui.item_card(ICON[row.material], f"{LABEL[row.material]} × {row.quantity}",
                            f"{row.owner} · {row.house} · {row.condition}{extra}", f"{row.weight_kg:.0f} kg",
                            f"{row.carbon_kg:.0f} kg CO₂e", chips)

    with tabs[0]:
        sub = open_l[open_l.route == "Reuse"]
        if sub.empty:
            st.info("No open requests fit the open listings in this radius.")
        for _, row in sub.iterrows():
            m = matched[row.id]
            ag = agreement(row.id, m.request)
            ready = both_agreed(row.id, m.request)
            tone = {"agreed": ("agreed", GREEN), "pending": ("pending", ORANGE)}
            chips = (ui.chip(f"Match {m.score}/100", LILAC) + " " + ui.chip(f"{m.distance_m} m apart", BLUE) + " "
                     + ui.chip(f"Donor {tone[ag['donor']][0]}", tone[ag["donor"]][1]) + " "
                     + ui.chip(f"Requester {tone[ag['requester']][0]}", tone[ag["requester"]][1]))
            c1, c2 = st.columns([6, 1.8], vertical_alignment="center")
            c1.html(ui.item_card(ICON[row.material], f"{LABEL[row.material]} × {row.quantity}",
                                 f"Donor: {row.owner} ({row.house}) → Requester: {m.receiver} ({m.receiver_house})",
                                 f"{row.weight_kg:.0f} kg", f"{row.carbon_kg:.0f} kg CO₂e", chips))
            if c2.button("Confirm hand-off" if ready else "Waiting for residents", key=f"ho_{row.id}",
                         type="primary" if ready else "secondary", disabled=not ready, width="stretch"):
                _confirm_handoff(row, m)
        if not sub.empty:
            st.caption("The confirm button unlocks only after both the donor and the requester agree on their Hand-offs page. "
                       "Match score = 40% material + 20% text similarity (TF-IDF) + 25% proximity + 15% quantity cover.")
    with tabs[1]:
        sub = open_l[open_l.route == "Salvage"]
        if sub.empty:
            st.info("Nothing waiting for salvage, or the staging zone is full.")
        for _, row in sub.iterrows():
            c1, c2 = st.columns([6, 1.6], vertical_alignment="center")
            c1.html(card(row, "", ui.chip(row.why, BLUE)))
            if c2.button("Drop at staging", key=f"st_{row.id}", width="stretch"):
                S.listings.loc[S.listings.id == row.id, "status"] = "staged"
                st.rerun()
    with tabs[2]:
        sub = open_l[open_l.route == "Recycle"]
        if sub.empty:
            st.info("Nothing queued for recycling.")
        for _, row in sub.iterrows():
            c1, c2 = st.columns([6, 1.6], vertical_alignment="center")
            c1.html(card(row, "", ui.chip(row.why, ORANGE)))
            if c2.button("Send to recycler", key=f"rc_{row.id}", width="stretch"):
                log_diversion(row, "Recycle", "Recycler")
                st.rerun()
    with tabs[3]:
        sub = open_l[open_l.route == "Landfill"]
        if sub.empty:
            st.success("No residual waste right now.")
        for _, row in sub.iterrows():
            st.html(card(row, "", ui.chip(row.why, "#7c7c6f")))
        if not sub.empty:
            st.caption("These stay in the skip bin. Fewer here means the routing is working.")
    with tabs[4]:
        staged = S.listings[S.listings.status == "staged"]
        if staged.empty:
            st.info("The staging zone is empty.")
        else:
            for _, row in staged.iterrows():
                st.html(card(row))
            if st.button("Run weekly salvage collection", type="primary"):
                for _, row in staged.iterrows():
                    log_diversion(row, "Salvage", "Salvage partner")
                st.toast(f"Collected {len(staged)} items.", icon="🚚")
                st.rerun()


def planner() -> None:
    ui.page_head("Township admin", "Handover planner",
                 "How much renovation waste will a handover wave create, and how much can you divert?")
    with st.container(border=True):
        c1, c2 = st.columns(2, gap="large")
        homes = c1.slider("Homes handed over", 50, 1000, 300, step=50)
        pct = c1.slider("Share renovating in the first months", 10, 100, 60, step=5, format="%d%%") / 100
        kg = c2.slider("Waste per renovating home (kg)", 200, 3000, 900, step=100)
        cap = c2.slider("Share of divertible waste you capture", 5, 100, 30, step=5, format="%d%%") / 100
    f = forecast(homes, pct, kg, cap)
    ui.kpis([("Expected renovation waste", round(f["waste_t"]), "tonnes", 0, ORANGE),
             (f"Divertible ({CFG['reusable_share']:.0%})", round(f["divertible_t"]), "tonnes", 0, LIME),
             ("Skip-bin loads avoided", round(f["bins_avoided"], 1), f"of {f['bins_total']:.0f}", 1, GREEN),
             ("Carbon avoided", round(f["carbon_t"], 1), "t CO₂e", 1, BLUE)])
    with st.container(border=True):
        _card_title("Where the waste ends up", "At this capture rate")
        st.altair_chart(charts.waste_stream(f), width="stretch", theme=None)
        per = f["diverted_t"] * 1000 / max(homes * pct, 1)
        st.markdown(f"**Planning use:** size the staging zone for about **{per:.0f} kg per renovating home**, book salvage and "
                    "recycler pickups for the handover weeks, and set a diversion target for the precinct.")
    ui.note(f"Every input is an assumption. The {CFG['reusable_share']:.0%} divertible share comes from a Malaysian housing-sector "
            "estimate (Ain Shams Engineering Journal, 2021) and may not match renovation waste. Replace waste per home with precinct data.")


def settings() -> None:
    ui.page_head("Township admin", "Settings", "The assumptions behind every number. Change them and the whole app updates.")
    c = S.cfg
    a, b = st.columns(2, gap="medium")
    with a:
        with st.container(border=True):
            _card_title("Operations")
            c["staging_capacity_kg"] = st.number_input("Staging zone capacity (kg)", 50, 5000, int(c["staging_capacity_kg"]), step=50)
            c["recycle_min_kg"] = st.number_input("Smallest batch a recycler collects (kg)", 1, 500, int(c["recycle_min_kg"]))
            c["skip_bin_kg"] = st.number_input("Waste in one skip-bin load (kg)", 500, 10000, int(c["skip_bin_kg"]), step=100)
            c["reusable_share"] = st.slider("Share of renovation waste that is divertible", 5, 80, int(c["reusable_share"] * 100), format="%d%%") / 100
    with b:
        with st.container(border=True):
            _card_title("Carbon and rewards")
            c["credit_Reuse"] = st.slider("Reuse carbon credit", 0, 100, int(c["credit_Reuse"] * 100), format="%d%%") / 100
            c["credit_Salvage"] = st.slider("Salvage carbon credit", 0, 100, int(c["credit_Salvage"] * 100), format="%d%%") / 100
            c["credit_Recycle"] = st.slider("Recycle carbon credit", 0, 100, int(c["credit_Recycle"] * 100), format="%d%%") / 100
            c["points_per_kg"] = st.number_input("Green points per kg CO₂e avoided", 1, 100, int(c["points_per_kg"]))
    CFG.update(c)
    if st.button("Reset to defaults"):
        S.cfg = dict(DEFAULT_CFG)
        CFG.update(S.cfg)
        st.rerun()
    ui.note("Credits and thresholds are placeholders until a recycler, salvage partner and the developer confirm real values.")


# =============================================================== BOTH
def method() -> None:
    ui.page_head("About", "Method and data", "How the numbers are produced, and what is still an assumption.")
    st.warning("All residents, listings and hand-offs are synthetic. The precinct is a made-up grid of 48 homes, 85 m apart.")
    with st.container(border=True):
        _card_title("Waste routing", "The first route that applies wins")
        st.markdown(
            "1. **Reuse:** an open neighbour request for the same material inside the radius.\n"
            f"2. **Salvage:** not worn out and the staging zone has room ({CFG['staging_capacity_kg']:.0f} kg). A partner collects weekly.\n"
            f"3. **Recycle:** the batch is at least {CFG['recycle_min_kg']:.0f} kg, the smallest a recycler will collect.\n"
            "4. **Landfill:** whatever is left stays in the skip bin.")
    with st.container(border=True):
        _card_title("Carbon estimate")
        st.markdown("`carbon avoided = weight × emission factor × condition credit × route credit`\n\n"
                    "Weight is quantity × an assumed kg per unit. Factors count the production stage (A1–A3) only. "
                    "Transport and end-of-life emissions are ignored.")
        cat = CATALOGUE.reset_index()
        cat["Material"] = cat.icon + " " + cat.label
        st.dataframe(cat[["Material", "unit", "kg_per_unit", "kgco2e_per_kg", "source"]].rename(columns={
            "unit": "Unit", "kg_per_unit": "kg per unit", "kgco2e_per_kg": "kg CO₂e per kg", "source": "Source"}),
            hide_index=True, width="stretch")
        ui.note("Emission factors are from the CIDB Malaysia inventory (2021, cradle-to-gate); where it lists a range, the lower value is used. "
                "The kg per unit is an assumption, because the inventory gives no unit weights.")
    with st.container(border=True):
        _card_title("Known limits")
        st.markdown("- Materials are picked by the user. A vision model to recognise them from a photo is not built.\n"
                    "- No real accounts or live backend: state lives in this browser session.\n"
                    "- The Resident and Township admin roles are a demo switch, not real sign-in. Residents answer hand-offs by acting as each person in turn.\n"
                    "- Agreement is two yes/no clicks. A live version would add reminders, time limits and a QR check-in at the guardhouse.\n"
                    "- Used fixtures need condition checks and a no-warranty notice before real use.")
