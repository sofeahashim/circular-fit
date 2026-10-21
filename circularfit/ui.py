"""Visual layer: GSAP-inspired dark theme, HTML components and motion."""
from __future__ import annotations

import html

import streamlit as st

GREEN, LIME, BLUE, LILAC, PINK, ORANGE = "#0ae448", "#abff84", "#00bae2", "#9d95ff", "#fec5fb", "#ff8709"
CREAM = "#fffce1"
ROUTE_COLOR = {"Reuse": GREEN, "Salvage": BLUE, "Recycle": ORANGE, "Landfill": "#7c7c6f"}
ROUTE_HELP = {
    "Reuse": "A neighbour asked for it",
    "Salvage": "Staged for weekly pickup",
    "Recycle": "Collected by a recycler",
    "Landfill": "Last resort",
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700;800;900&display=swap');
:root{--bg:#0e100f;--surface:#161918;--surface2:#1e2220;--line:rgba(255,252,225,.13);--cream:#fffce1;
--muted:rgba(255,252,225,.62);--green:#0ae448;--lime:#abff84;--blue:#00bae2;--lilac:#9d95ff;--pink:#fec5fb;--orange:#ff8709;
--grad:linear-gradient(114deg,#0ae448 20%,#abff84 66%)}
html,body,.stApp,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--cream)}
.stApp, .stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp button, .stApp input,
.stApp textarea, .stApp td, .stApp th, .stApp a, .stApp [data-baseweb]{font-family:'Hanken Grotesk',system-ui,sans-serif!important}
[data-testid="stMainBlockContainer"]{max-width:1200px;padding:4.6rem 2rem 6rem}
[data-testid="stHeader"]{background:rgba(14,16,15,.82);backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
[data-testid="stToolbarActions"],[data-testid="stAppDeployButton"],[data-testid="stMainMenu"],[data-testid="stDecoration"],#MainMenu,footer{display:none!important}
h1,h2,h3{letter-spacing:-.03em;font-weight:700}
a{color:var(--green)}

/* ---------- top navigation ---------- */
[data-testid="stHeader"] a, [data-testid="stHeader"] button{border-radius:999px!important;font-weight:600!important;color:var(--cream)!important}
[data-testid="stHeader"] a:hover{background:rgba(255,252,225,.08)!important}
[data-testid="stHeader"] a[aria-current="page"], [data-testid="stHeader"] [data-testid="stTopNavLinkActive"]{
  background:var(--cream)!important;color:#0e100f!important}
[data-testid="stHeader"] a[aria-current="page"] *{color:#0e100f!important}

/* ---------- buttons ---------- */
.stButton>button,.stDownloadButton>button,[data-testid="stPageLink-NavLink"],[data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-primary"]{
  border-radius:999px!important;padding:.55rem 1.3rem!important;font-weight:700!important;letter-spacing:-.01em;
  transition:transform .15s ease,box-shadow .2s ease,background .2s ease;min-height:2.7rem}
[data-testid="stBaseButton-primary"]{background:var(--grad)!important;color:#0e100f!important;border:0!important}
[data-testid="stBaseButton-primary"] *{color:#0e100f!important}
[data-testid="stBaseButton-primary"]:hover{transform:translateY(-2px);box-shadow:0 10px 30px -8px rgba(10,228,72,.55)}
[data-testid="stBaseButton-secondary"],.stDownloadButton>button,[data-testid="stPageLink-NavLink"]{
  background:transparent!important;border:1.5px solid rgba(10,228,72,.7)!important;color:var(--cream)!important}
[data-testid="stBaseButton-secondary"]:hover,.stDownloadButton>button:hover,[data-testid="stPageLink-NavLink"]:hover{
  background:rgba(10,228,72,.12)!important;transform:translateY(-2px)}
[data-testid="stBaseButton-secondary"]:disabled,[data-testid="stBaseButton-primary"]:disabled{opacity:.4}

/* ---------- inputs ---------- */
[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="select"]>div,[data-baseweb="textarea"]{
  background:var(--surface2)!important;border-radius:14px!important;border-color:var(--line)!important}
[data-baseweb="input"]:focus-within,[data-baseweb="select"]:focus-within>div{border-color:var(--green)!important;box-shadow:0 0 0 3px rgba(10,228,72,.18)}
[data-testid="stWidgetLabel"] p,label p{font-weight:600;color:var(--muted);font-size:.86rem}
[data-testid="stFileUploaderDropzone"]{background:var(--surface2);border:1.5px dashed rgba(10,228,72,.5);border-radius:18px}
[data-testid="stNumberInput"] button{border-radius:10px}

/* ---------- sliders ---------- */
[data-testid="stSlider"]{padding:.2rem .6rem 0}
[data-testid="stSlider"] [data-testid="stWidgetLabel"]{margin-bottom:1.7rem}
[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child{height:10px!important;border-radius:999px!important}
[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child > div{height:10px!important;border-radius:999px!important}
[data-testid="stSlider"] [role="slider"]{width:26px!important;height:26px!important;border-radius:50%!important;
  background:var(--cream)!important;border:5px solid var(--green)!important;box-shadow:0 0 0 6px rgba(10,228,72,.18),0 6px 18px rgba(0,0,0,.45)!important;
  transition:box-shadow .2s ease,transform .15s ease}
[data-testid="stSlider"] [role="slider"]:hover,[data-testid="stSlider"] [role="slider"]:focus{
  transform:scale(1.12);box-shadow:0 0 0 10px rgba(10,228,72,.22),0 6px 18px rgba(0,0,0,.45)!important}
[data-testid="stSliderThumbValue"]{background:var(--grad);color:#0e100f!important;border-radius:999px;padding:2px 10px;font-weight:800;top:-34px!important}
[data-testid="stSliderThumbValue"] *{color:#0e100f!important}
[data-testid="stSliderTickBarMin"],[data-testid="stSliderTickBarMax"]{color:var(--muted);font-weight:600}

/* ---------- tabs / segmented ---------- */
[data-baseweb="tab-list"]{gap:8px;background:transparent;border:0}
[data-baseweb="tab"]{border-radius:999px!important;padding:.45rem 1.1rem!important;background:var(--surface2)!important;
  border:1px solid var(--line)!important;font-weight:700!important;height:auto!important}
[data-baseweb="tab"][aria-selected="true"]{background:var(--cream)!important;color:#0e100f!important}
[data-baseweb="tab"][aria-selected="true"] *{color:#0e100f!important}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none!important}
[data-testid="stButtonGroup"] [role="radiogroup"]{gap:4px}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"]{border:0!important;background:transparent!important;border-radius:999px!important;
  color:var(--muted)!important;font-weight:700!important;padding:.45rem 1.25rem!important}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"] *{color:inherit!important}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"][aria-checked="true"]{background:var(--cream)!important;color:#0e100f!important}
[data-testid="stButtonGroup"]:has(button[data-variant="segmented_control"]) [role="radiogroup"]{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:4px;width:fit-content}
[data-testid="stButtonGroup"] button[data-variant="pills"]{border-radius:999px!important;background:var(--surface2)!important;border:1px solid var(--line)!important;
  color:var(--cream)!important;font-weight:600!important}
[data-testid="stButtonGroup"] button[data-variant="pills"][aria-checked="true"]{background:var(--grad)!important;color:#0e100f!important;border-color:transparent!important}
[data-testid="stButtonGroup"] button[data-variant="pills"][aria-checked="true"] *{color:#0e100f!important}

/* ---------- containers ---------- */
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:22px!important;background:var(--surface);border-color:var(--line)!important}
[data-testid="stProgress"] > div > div{background:var(--surface2)!important;border-radius:999px;height:12px}
[data-testid="stProgress"] [role="progressbar"] > div{background:var(--grad)!important;border-radius:999px}
[data-testid="stAlert"]{border-radius:16px;background:var(--surface2);border:1px solid var(--line)}
[data-testid="stDataFrame"]{border-radius:16px;overflow:hidden}
[data-testid="stPopover"] button{border-radius:999px!important}
hr{border-color:var(--line)!important}

/* ---------- components ---------- */
.cf-eyebrow{display:inline-flex;gap:8px;align-items:center;font-weight:700;font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:var(--green)}
.cf-eyebrow:before{content:"";width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 12px var(--green)}
.cf-hero{position:relative;padding:2.2rem 0 1.4rem;overflow:hidden}
.cf-hero h1{font-size:clamp(2.8rem,7.5vw,6rem);line-height:.95;letter-spacing:-.045em;font-weight:600;margin:.8rem 0 1.2rem;color:var(--cream)}
.cf-hero h1 span{display:block}
.cf-hero h1 span:nth-child(2){padding-left:min(10vw,9rem)}
.cf-hero h1 em{font-style:normal;background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.cf-lead{font-size:1.15rem;color:var(--muted);max-width:40rem;line-height:1.5}
.cf-blob{position:absolute;right:4%;top:12%;width:min(26vw,300px);aspect-ratio:1;border-radius:42% 58% 55% 45%/50% 42% 58% 50%;
  background:conic-gradient(from 90deg,#0ae448,#abff84,#00bae2,#9d95ff,#fec5fb,#0ae448);filter:blur(1px);opacity:.9;animation:cfspin 18s linear infinite,cfmorph 9s ease-in-out infinite}
@keyframes cfspin{to{transform:rotate(360deg)}}
@keyframes cfmorph{50%{border-radius:58% 42% 45% 55%/42% 58% 42% 58%}}
@media (max-width:760px){.cf-blob{display:none}.cf-hero h1 span:nth-child(2){padding-left:0}}
.cf-head{margin:.6rem 0 1.4rem}
.cf-head h1{font-size:clamp(2rem,4.5vw,3.3rem);letter-spacing:-.04em;line-height:1;margin:.5rem 0 .6rem;font-weight:600}
.cf-head p{color:var(--muted);max-width:42rem;margin:0;font-size:1.05rem}
.cf-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:.4rem 0 1.2rem}
.cf-kpi{background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:18px 20px;position:relative;overflow:hidden}
.cf-kpi:after{content:"";position:absolute;right:-30px;top:-30px;width:110px;height:110px;border-radius:50%;background:var(--accent,var(--green));opacity:.16;filter:blur(8px)}
.cf-kpi small{display:block;color:var(--muted);font-weight:600;font-size:.82rem}
.cf-kpi b{display:block;font-size:2.7rem;letter-spacing:-.05em;line-height:1.05;font-weight:600;margin-top:6px}
.cf-kpi b i{font-style:normal;font-size:1rem;color:var(--muted);letter-spacing:0;margin-left:6px;font-weight:600}
.cf-kpi .bar{height:4px;border-radius:99px;background:var(--accent,var(--green));margin-top:12px;width:42%}
.cf-card{background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:20px 22px}
.cf-card h3{margin:0 0 4px;font-size:1.15rem}
.cf-card p{margin:0;color:var(--muted);font-size:.94rem;line-height:1.5}
.cf-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}
.cf-action{display:block;background:var(--surface);border:1px solid var(--line);border-radius:26px;padding:24px;min-height:190px;position:relative;overflow:hidden;transition:transform .25s ease,border-color .25s ease}
.cf-action:hover{transform:translateY(-5px);border-color:var(--accent,var(--green))}
.cf-action .n{font-size:.8rem;font-weight:800;letter-spacing:.1em;color:var(--accent,var(--green))}
.cf-action h3{font-size:1.7rem;letter-spacing:-.04em;margin:.6rem 0 .4rem;line-height:1.05;font-weight:600}
.cf-action p{color:var(--muted);margin:0}
.cf-action:before{content:"";position:absolute;right:-40px;bottom:-40px;width:150px;height:150px;border-radius:50%;background:var(--accent,var(--green));opacity:.18;filter:blur(10px)}
.cf-chip{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:3px 11px;font-size:.78rem;font-weight:700;
  background:rgba(255,252,225,.08);color:var(--cream);border:1px solid var(--line)}
.cf-chip i{width:8px;height:8px;border-radius:50%;background:var(--c,var(--green));display:inline-block}
.cf-item{background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:16px 18px;display:grid;grid-template-columns:54px 1fr auto;gap:14px;align-items:center;margin-bottom:10px}
.cf-item .ic{width:54px;height:54px;border-radius:16px;display:grid;place-items:center;font-size:1.6rem;background:linear-gradient(145deg,rgba(10,228,72,.25),rgba(0,186,226,.2))}
.cf-item b{font-size:1.02rem;letter-spacing:-.01em}
.cf-item span.m{display:block;color:var(--muted);font-size:.86rem;margin-top:2px}
.cf-item .r{text-align:right;font-weight:700}
.cf-item .r small{display:block;color:var(--muted);font-weight:600}
.cf-meter{margin:.2rem 0 .8rem}
.cf-meter .t{display:flex;justify-content:space-between;font-weight:700;font-size:.9rem}
.cf-meter .t span{color:var(--muted);font-weight:600}
.cf-meter .tr{height:14px;border-radius:99px;background:var(--surface2);overflow:hidden;margin-top:8px}
.cf-meter .tr i{display:block;height:100%;border-radius:99px;background:var(--grad)}
.cf-flow{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;position:relative}
.cf-step{background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:18px;position:relative}
.cf-step .k{width:34px;height:34px;border-radius:50%;display:grid;place-items:center;font-weight:800;background:var(--grad);color:#0e100f;margin-bottom:12px}
.cf-step b{display:block;font-size:1.05rem;letter-spacing:-.02em}
.cf-step span{display:block;color:var(--muted);font-size:.86rem;margin-top:3px;line-height:1.4}
.cf-step:not(:last-child):after{content:"";position:absolute;right:-13px;top:34px;width:14px;height:2px;background:var(--green);opacity:.7;z-index:2}
.cf-routes{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:12px}
.cf-route{border-radius:20px;padding:14px 16px;border:1px solid var(--line);background:var(--surface2);border-top:4px solid var(--c)}
.cf-route b{display:block}.cf-route span{color:var(--muted);font-size:.84rem}
@media (max-width:900px){.cf-flow{grid-template-columns:1fr 1fr}.cf-routes{grid-template-columns:1fr 1fr}.cf-step:after{display:none}}
.cf-pts{font-size:4.2rem;font-weight:600;letter-spacing:-.06em;line-height:1;background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.cf-note{background:rgba(255,135,9,.1);border:1px solid rgba(255,135,9,.35);border-radius:16px;padding:12px 16px;color:#ffd9b0;font-size:.9rem}
.cf-brand{display:inline-flex;align-items:center;gap:10px;font-weight:700;font-size:1.25rem;letter-spacing:-.04em}
.cf-brand:before{content:"";width:28px;height:28px;border-radius:50%;background:conic-gradient(from 20deg,#0ae448,#abff84 60%,transparent 62%,transparent 70%,#0ae448 72%);-webkit-mask:radial-gradient(circle,transparent 8px,#000 9px);mask:radial-gradient(circle,transparent 8px,#000 9px)}
.cf-reveal{opacity:0;transform:translateY(18px)}
"""

LOGO = '<span class="cf-brand">CircularFit</span>'

JS = """
(function(){
  if(!window.__cfBoot){
    window.__cfBoot=true;
    var s=document.createElement('script');
    s.src='https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js';
    s.onload=function(){window.cfRun&&window.cfRun();};
    document.head.appendChild(s);
    window.cfRun=function(){
      document.querySelectorAll('.cf-count:not([data-done])').forEach(function(el){
        el.setAttribute('data-done','1');
        var to=parseFloat(el.dataset.to||'0'),dec=parseInt(el.dataset.dec||'0');
        var fmt=function(v){return v.toLocaleString(undefined,{minimumFractionDigits:dec,maximumFractionDigits:dec});};
        if(window.gsap){var o={v:0};gsap.to(o,{v:to,duration:1.4,ease:'power3.out',onUpdate:function(){el.textContent=fmt(o.v);}});}
        else{el.textContent=fmt(to);}
      });
      document.querySelectorAll('.cf-reveal:not([data-done])').forEach(function(el,i){
        el.setAttribute('data-done','1');
        if(window.gsap){gsap.to(el,{opacity:1,y:0,duration:.7,delay:Math.min(i*.06,.5),ease:'power3.out'});}
        else{el.style.opacity=1;el.style.transform='none';}
      });
    };
    new MutationObserver(function(){clearTimeout(window.__cfT);window.__cfT=setTimeout(window.cfRun,60);})
      .observe(document.body,{childList:true,subtree:true});
  }
  setTimeout(function(){window.cfRun&&window.cfRun();},80);
})();
"""


def inject() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    st.html(f"<script>{JS}</script>", unsafe_allow_javascript=True)


def esc(x) -> str:
    return html.escape(str(x))


def hero(eyebrow: str, lines: list[str], lead: str) -> None:
    spans = "".join(f"<span>{l}</span>" for l in lines)
    st.html(f'<div class="cf-hero"><div class="cf-blob"></div><div class="cf-eyebrow">{esc(eyebrow)}</div>'
            f'<h1>{spans}</h1><p class="cf-lead">{esc(lead)}</p></div>')


def page_head(eyebrow: str, title: str, sub: str = "") -> None:
    st.html(f'<div class="cf-head cf-reveal"><div class="cf-eyebrow">{esc(eyebrow)}</div><h1>{esc(title)}</h1>'
            + (f"<p>{esc(sub)}</p>" if sub else "") + "</div>")


def kpis(items: list[tuple]) -> None:
    """items: (label, value, unit, decimals, accent)"""
    cards = ""
    for label, value, unit, dec, accent in items:
        cards += (f'<div class="cf-kpi cf-reveal" style="--accent:{accent}"><small>{esc(label)}</small>'
                  f'<b><span class="cf-count" data-to="{value}" data-dec="{dec}">0</span><i>{esc(unit)}</i></b>'
                  f'<div class="bar"></div></div>')
    st.html(f'<div class="cf-kpis">{cards}</div>')


def chip(text: str, color: str = GREEN) -> str:
    return f'<span class="cf-chip" style="--c:{color}"><i></i>{esc(text)}</span>'


def item_card(icon: str, title: str, meta: str, right_top: str, right_sub: str, chips: str = "") -> str:
    return (f'<div class="cf-item cf-reveal"><div class="ic">{icon}</div><div><b>{esc(title)}</b>'
            f'<span class="m">{esc(meta)}</span>{("<div style=margin-top:6px>" + chips + "</div>") if chips else ""}</div>'
            f'<div class="r">{esc(right_top)}<small>{esc(right_sub)}</small></div></div>')


def meter(label: str, value: float, maximum: float, right: str) -> None:
    pct = max(0, min(100, 100 * value / maximum)) if maximum else 0
    st.html(f'<div class="cf-meter"><div class="t">{esc(label)}<span>{esc(right)}</span></div>'
            f'<div class="tr"><i style="width:{pct:.0f}%"></i></div></div>')


def action_card(n: str, title: str, text: str, accent: str) -> str:
    return (f'<div class="cf-action cf-reveal" style="--accent:{accent}"><div class="n">{n}</div>'
            f"<h3>{esc(title)}</h3><p>{esc(text)}</p></div>")


def flow() -> None:
    steps = [("1", "Log", "Owner or contractor logs leftovers and strip-out items."),
             ("2", "Estimate", "Weight and carbon saved come from a catalogue."),
             ("3", "Route", "Each item takes the best route available."),
             ("4", "Record", "Every diverted item goes into the ledger."),
             ("5", "Report", "Dashboard for the developer, points for residents.")]
    s = "".join(f'<div class="cf-step cf-reveal"><div class="k">{k}</div><b>{t}</b><span>{d}</span></div>' for k, t, d in steps)
    r = "".join(f'<div class="cf-route cf-reveal" style="--c:{ROUTE_COLOR[k]}"><b>{k}</b><span>{ROUTE_HELP[k]}</span></div>'
                for k in ROUTE_COLOR)
    st.html(f'<div class="cf-flow">{s}</div><div class="cf-routes">{r}</div>')


def note(text: str) -> None:
    st.html(f'<div class="cf-note">{text}</div>')


def brand() -> str:
    return LOGO
