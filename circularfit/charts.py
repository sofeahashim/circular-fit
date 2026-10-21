"""Altair charts styled for the dark CircularFit theme (brand gradients, rounded marks, no gridlines)."""
from __future__ import annotations

import altair as alt
import pandas as pd

from .core import ROUTE_ORDER
from .ui import BLUE, CREAM, GREEN, LILAC, LIME, ORANGE, PINK, ROUTE_COLOR

FONT = "Hanken Grotesk"
MUTED = "#bbbaa6"


def _theme():
    return {"config": {
        "background": "transparent",
        "view": {"stroke": None},
        "font": FONT,
        "axis": {"labelColor": MUTED, "titleColor": MUTED, "labelFont": FONT, "titleFont": FONT, "labelFontSize": 12,
                 "titleFontSize": 12, "titleFontWeight": 600, "domain": False, "tickColor": "transparent",
                 "gridColor": "rgba(255,252,225,.08)", "gridDash": [2, 4]},
        "legend": {"labelColor": CREAM, "titleColor": MUTED, "labelFont": FONT, "titleFont": FONT, "labelFontSize": 12,
                   "symbolType": "circle", "symbolSize": 120, "orient": "bottom", "direction": "horizontal"},
        "title": {"color": CREAM, "font": FONT},
    }}


alt.themes.register("circularfit", _theme)
alt.themes.enable("circularfit")


def _grad(c1: str, c2: str, horizontal: bool = True) -> alt.Gradient:
    return alt.Gradient(gradient="linear", stops=[alt.GradientStop(color=c1, offset=0), alt.GradientStop(color=c2, offset=1)],
                        x1=0, x2=1 if horizontal else 0, y1=0, y2=0 if horizontal else 1)


def donut_routes(led: pd.DataFrame, height: int = 280) -> alt.LayerChart:
    d = led.groupby("route", as_index=False).weight_kg.sum()
    d["share"] = d.weight_kg / d.weight_kg.sum()
    total = f"{d.weight_kg.sum():,.0f} kg"
    scale = alt.Scale(domain=ROUTE_ORDER, range=[ROUTE_COLOR[r] for r in ROUTE_ORDER])
    arc = alt.Chart(d).mark_arc(innerRadius=78, outerRadius=118, cornerRadius=9, padAngle=0.03).encode(
        theta=alt.Theta("weight_kg:Q", stack=True),
        color=alt.Color("route:N", scale=scale, legend=alt.Legend(title=None)),
        order=alt.Order("route:N", sort="ascending"),
        tooltip=[alt.Tooltip("route:N", title="Route"), alt.Tooltip("weight_kg:Q", title="kg", format=",.0f"),
                 alt.Tooltip("share:Q", title="Share", format=".0%")])
    centre = alt.Chart(pd.DataFrame({"t": [total], "s": ["diverted"]}))
    big = centre.mark_text(fontSize=30, fontWeight=600, color=CREAM, dy=-8, font=FONT).encode(text="t:N")
    small = centre.mark_text(fontSize=13, color=MUTED, dy=18, font=FONT).encode(text="s:N")
    return (arc + big + small).properties(height=height)


def bars_carbon(led: pd.DataFrame, labels: dict, height: int = 260) -> alt.LayerChart:
    d = led.assign(Material=led.material.map(labels)).groupby("Material", as_index=False)[["weight_kg", "carbon_kg"]].sum()
    base = alt.Chart(d).encode(y=alt.Y("Material:N", sort="-x", title=None, axis=alt.Axis(labelLimit=220, labelFontSize=13)),
                               x=alt.X("carbon_kg:Q", title=None, axis=alt.Axis(grid=True, labels=False)))
    bars = base.mark_bar(cornerRadiusEnd=12, height=22, color=_grad(GREEN, LIME)).encode(
        tooltip=["Material", alt.Tooltip("carbon_kg:Q", title="kg CO₂e", format=".1f"), alt.Tooltip("weight_kg:Q", title="kg", format=".0f")])
    text = base.mark_text(align="left", dx=8, color=CREAM, fontWeight=600, fontSize=13, font=FONT).encode(
        text=alt.Text("carbon_kg:Q", format=".1f"))
    return (bars + text).properties(height=height)


def area_cumulative(led: pd.DataFrame, height: int = 260) -> alt.LayerChart:
    t = led.groupby("day", as_index=False).weight_kg.sum().sort_values("day")
    t["cum"] = t.weight_kg.cumsum()
    base = alt.Chart(t).encode(x=alt.X("day:Q", title="Day of handover month", axis=alt.Axis(grid=False, tickMinStep=1)),
                               y=alt.Y("cum:Q", title="kg diverted"))
    area = base.mark_area(interpolate="monotone", line=False,
                          color=alt.Gradient(gradient="linear", x1=0, x2=0, y1=0, y2=1, stops=[
                              alt.GradientStop(color="rgba(10,228,72,.55)", offset=0), alt.GradientStop(color="rgba(10,228,72,0)", offset=1)]))
    line = base.mark_line(interpolate="monotone", strokeWidth=3, color=LIME)
    pts = base.mark_point(filled=True, size=90, color=CREAM, stroke=GREEN, strokeWidth=3).encode(
        tooltip=[alt.Tooltip("day:Q", title="Day"), alt.Tooltip("cum:Q", title="kg so far", format=".0f")])
    return (area + line + pts).properties(height=height)


def precinct_map(houses: pd.DataFrame, listings: pd.DataFrame, requests: pd.DataFrame, me_house: str, height: int = 360) -> alt.LayerChart:
    H = houses.copy()
    nl = listings[listings.status == "open"].groupby("house").size().rename("listings")
    nr = requests[requests.status == "open"].groupby("house").size().rename("requests")
    H = H.join(nl, on="house").join(nr, on="house").fillna(0)
    H["status"] = "Home"
    H.loc[H.listings > 0, "status"] = "Has waste to divert"
    H.loc[H.requests > 0, "status"] = "Needs materials"
    H.loc[(H.listings > 0) & (H.requests > 0), "status"] = "Both"
    H["you"] = H.house == me_house
    order = ["Home", "Has waste to divert", "Needs materials", "Both"]
    scale = alt.Scale(domain=order, range=["#3a3d38", GREEN, ORANGE, LILAC])
    enc = dict(
        x=alt.X("x:Q", axis=None, scale=alt.Scale(padding=20)),
        y=alt.Y("y:Q", axis=None, scale=alt.Scale(reverse=True, padding=20)),
        color=alt.Color("status:N", scale=scale, legend=alt.Legend(title=None)),
        tooltip=["house", "status", alt.Tooltip("listings:Q", format=".0f"), alt.Tooltip("requests:Q", format=".0f")])
    glow = alt.Chart(H[H.status != "Home"]).mark_circle(size=1500, opacity=0.14).encode(**enc)
    dots = alt.Chart(H).mark_circle(size=330, opacity=0.95).encode(**enc)
    ring = alt.Chart(H[H.you]).mark_point(shape="circle", size=900, filled=False, strokeWidth=2.5, color=CREAM).encode(
        x="x:Q", y="y:Q")
    return (glow + dots + ring).properties(height=height)


def waste_stream(f: dict, height: int = 120) -> alt.Chart:
    d = pd.DataFrame({
        "stream": ["Stays in skip bins", "Divertible, not captured", "Diverted by CircularFit"],
        "tonnes": [f["waste_t"] - f["divertible_t"], f["divertible_t"] - f["diverted_t"], f["diverted_t"]],
        "order": [0, 1, 2], "all": ["Renovation waste"] * 3})
    scale = alt.Scale(domain=list(d.stream), range=["#4a4d46", ORANGE, GREEN])
    return alt.Chart(d).mark_bar(cornerRadius=10, height=44).encode(
        x=alt.X("tonnes:Q", stack="zero", title="tonnes", axis=alt.Axis(grid=True)),
        y=alt.Y("all:N", title=None, axis=None),
        color=alt.Color("stream:N", scale=scale, legend=alt.Legend(title=None)),
        order=alt.Order("order:Q"),
        tooltip=[alt.Tooltip("stream:N", title="Stream"), alt.Tooltip("tonnes:Q", format=".1f")]).properties(height=height)


def points_bars(board: pd.DataFrame, height: int = 260) -> alt.LayerChart:
    base = alt.Chart(board).encode(y=alt.Y("Resident:N", sort="-x", title=None, axis=alt.Axis(labelFontSize=13)),
                                   x=alt.X("Points:Q", title=None, axis=alt.Axis(labels=False)))
    bars = base.mark_bar(cornerRadiusEnd=12, height=20, color=_grad(LILAC, PINK)).encode(
        tooltip=["Resident", alt.Tooltip("Points:Q", format=",.0f")])
    text = base.mark_text(align="left", dx=8, color=CREAM, fontWeight=600, font=FONT).encode(text=alt.Text("Points:Q", format=",.0f"))
    return (bars + text).properties(height=height)
