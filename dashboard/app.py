"""
FIFA World Cup 2026 — Player Analysis Dashboard
------------------------------------------------
A single-file Streamlit dashboard. Visual identity: "Floodlight" —
a premium night-match aesthetic built entirely from one warm-orange
family, from deep near-black ember tones through to light peach,
gold and cream. No colors outside that family are used anywhere,
including the charts, tables, and info cards.

Run from the project root:
    streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import streamlit as st

# ----------------------------------------------------------------------------
# Path setup — lets us import the analysis package from the project root
# ----------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from analysis.stats import summary_stats, top_n
except Exception:
    def top_n(df, column, n=10):
        return df[["Player", column]].sort_values(by=column, ascending=False).head(n)

    def summary_stats(df):
        return {
            "describe": df.describe(),
            "mean": df.mean(numeric_only=True),
            "median": df.median(numeric_only=True),
            "std": df.std(numeric_only=True),
            "var": df.var(numeric_only=True),
            "min": df.min(numeric_only=True),
            "max": df.max(numeric_only=True),
        }

DATA_PATH = ROOT_DIR / "data" / "players_cleaned.csv"

KEY_STATS = [
    "Assists",
    "Attempts At Goal",
    "Passes",
    "Passing Accuracy (%)",
    "Top Speed (km/h)",
    "Total Distance (m)",
    "Goal Contribution",
    "Goal Efficiency",
    "xG Efficiency",
    "Player Involvements",
]

# ============================================================================
# 1. PALETTE — "Premium Floodlight". One warm-orange family, spanning
#    near-black embers up through rust, blaze, amber and gold, all the way
#    to cream — so the UI reads alive instead of one flat brown tone.
# ============================================================================
VOID = "#150C06"       # deepest background depth (chart canvas)
VOID_2 = "#1D110A"
BG = "#24140B"          # app background
EMBER = "#3A1F12"       # dark card surface
EMBER_2 = "#4A2916"     # dark card surface, one step lighter (hover / alt rows)
LINE = "#5A3419"        # borders / dividers
RUST = "#C2530E"        # deep accent
BLAZE = "#FF6A1A"       # primary highlight
AMBER = "#FFB347"       # secondary highlight
GOLD = "#FFC65C"        # golden accent
LIGHT_ORANGE = "#FFD39A"
PEACH = "#FFE8C6"       # soft peach (light card surface)
CREAM = "#FFF3DE"       # main light text / cream
CREAM_DIM = "#C99A6E"   # dimmed body text on dark surfaces
INK = "#3A1A08"         # dark text used on light-orange surfaces
HERO_START = "#3A1C0E"
HERO_END = "#7A3E16"

ACCENTS = [BLAZE, AMBER, GOLD, RUST]  # cycled across cards / badges for variety
ORANGE_CMAP = LinearSegmentedColormap.from_list("floodlight", [RUST, BLAZE, AMBER, GOLD])

# ============================================================================
# 2. PAGE CONFIG + GLOBAL CSS
# ============================================================================
st.set_page_config(
    page_title="FIFA World Cup 2026 · Player Analysis",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {{
        --void: {VOID}; --void2: {VOID_2}; --bg: {BG}; --ember: {EMBER}; --ember2: {EMBER_2};
        --line: {LINE}; --rust: {RUST}; --blaze: {BLAZE}; --amber: {AMBER};
        --gold: {GOLD}; --lightorange: {LIGHT_ORANGE}; --peach: {PEACH}; --cream: {CREAM};
        --creamdim: {CREAM_DIM}; --ink: {INK}; --herostart: {HERO_START}; --heroend: {HERO_END};
    }}

    html, body, [class*="css"] {{ font-family: 'Manrope', sans-serif; }}

    .stApp {{
        background:
            radial-gradient(ellipse 900px 500px at 15% -8%, rgba(255,106,26,0.14), transparent 60%),
            radial-gradient(ellipse 700px 500px at 100% 10%, rgba(255,179,71,0.09), transparent 55%),
            var(--bg);
        color: var(--cream);
    }}

    #MainMenu, footer {{ visibility: hidden; }}
    /* Keep the header — the sidebar open/close arrow lives inside it —
       but make it blend into the page instead of showing Streamlit's bar. */
    header[data-testid="stHeader"] {{
        background: transparent;
        box-shadow: none;
    }}
    [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] {{
        color: var(--cream) !important;
        background: linear-gradient(135deg, var(--blaze), var(--rust)) !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 14px rgba(255,106,26,0.35);
    }}
    [data-testid="stSidebarCollapsedControl"] svg, [data-testid="collapsedControl"] svg {{
        fill: #150B06 !important;
    }}
    header[data-testid="stHeader"] button svg {{
        fill: var(--cream) !important;
    }}
    header[data-testid="stHeader"] button:hover svg {{
        fill: var(--blaze) !important;
    }}
    .block-container {{ padding-top: 1.8rem; padding-bottom: 3.5rem; max-width: 1420px; }}

    h1, h2, h3, h4 {{
        font-family: 'Rajdhani', sans-serif !important;
        color: var(--cream) !important;
        letter-spacing: 0.02em;
        font-weight: 700 !important;
    }}
    p, span, label, div {{ color: var(--cream); }}

    /* ================= SIDEBAR ================= */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, var(--void2) 0%, var(--ember) 100%);
        border-right: 1px solid var(--line);
    }}
    section[data-testid="stSidebar"] .block-container {{ padding-top: 1.3rem; padding-left: 1.1rem; padding-right: 1.1rem; }}

    .fl-logo {{
        display: flex; align-items: center; gap: 0.6rem;
        padding: 0.4rem 0.2rem 1.1rem 0.2rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.1rem;
    }}
    .fl-logo .ball {{
        width: 40px; height: 40px; border-radius: 50%; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center; font-size: 1.35rem;
        background: linear-gradient(135deg, var(--blaze), var(--rust));
        box-shadow: 0 0 18px rgba(255,106,26,0.55);
    }}
    .fl-logo .txt-main {{
        font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 1.18rem;
        color: var(--cream); line-height: 1.1;
    }}
    .fl-logo .txt-sub {{
        font-family: 'JetBrains Mono', monospace; font-size: 0.66rem; letter-spacing: 0.14em;
        text-transform: uppercase; color: var(--gold);
    }}

    .fl-side-heading {{
        font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 0.92rem;
        letter-spacing: 0.16em; text-transform: uppercase; color: var(--gold);
        margin: 0.2rem 0 0.7rem 0; display: flex; align-items: center; gap: 0.4rem;
    }}
    .fl-side-heading::before {{
        content: ""; width: 6px; height: 6px; border-radius: 50%;
        background: var(--blaze); box-shadow: 0 0 8px rgba(255,106,26,0.9);
    }}

    /* ---- sidebar nav rendered from st.radio, styled as a menu list ---- */
    div[data-testid="stSidebar"] div[data-testid="stRadio"] > div {{
        flex-direction: column; gap: 3px;
    }}
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
        background: transparent;
        border: 1px solid transparent;
        border-radius: 10px;
        padding: 0.55rem 0.75rem;
        margin: 0 !important;
        cursor: pointer;
        transition: background 0.18s ease, border-color 0.18s ease, transform 0.15s ease;
        width: 100%;
    }}
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
        background: var(--ember2);
        border-color: var(--line);
        transform: translateX(2px);
    }}
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-child {{
        display: none;
    }}
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label p {{
        font-family: 'Rajdhani', sans-serif; font-weight: 600; font-size: 0.98rem;
        letter-spacing: 0.02em; color: var(--creamdim);
        transition: color 0.18s ease;
    }}
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {{
        background: linear-gradient(135deg, var(--blaze), var(--rust));
        box-shadow: 0 4px 16px rgba(255,106,26,0.35);
    }}
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {{
        color: #150B06 !important; font-weight: 700 !important;
    }}
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked):hover {{
        transform: none;
    }}

    .fl-side-divider {{ height: 1px; background: var(--line); margin: 1.15rem 0; border: none; }}

    /* ---- buttons / inputs ---- */
    .stButton>button, .stDownloadButton>button {{
        background: linear-gradient(135deg, var(--blaze), var(--rust));
        color: #150B06; border: none; border-radius: 9px; font-weight: 700;
        font-family: 'Rajdhani', sans-serif; letter-spacing: 0.04em;
        text-transform: uppercase; padding: 0.6rem 1.1rem;
        box-shadow: 0 4px 14px rgba(255,106,26,0.28);
        transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
    }}
    .stButton>button:hover, .stDownloadButton>button:hover {{
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 10px 26px rgba(255,106,26,0.5);
        background: linear-gradient(135deg, var(--amber), var(--blaze));
        color: #150B06;
    }}
    .stButton>button:active, .stDownloadButton>button:active {{
        transform: translateY(0px) scale(0.99);
    }}

    div[data-baseweb="select"] > div, .stTextInput input, .stMultiSelect div[data-baseweb="select"] {{
        background-color: var(--ember) !important;
        border: 1px solid var(--line) !important;
        color: var(--cream) !important;
        border-radius: 8px !important;
        transition: border-color 0.18s ease;
    }}
    div[data-baseweb="select"] > div:focus-within, .stTextInput input:focus {{
        border-color: var(--blaze) !important;
        box-shadow: 0 0 0 2px rgba(255,106,26,0.18) !important;
    }}
    .stSlider [data-baseweb="slider"] div {{ background: var(--line); }}
    .stSlider [role="slider"] {{ background: var(--blaze) !important; border-color: var(--blaze) !important;
        box-shadow: 0 0 10px rgba(255,106,26,0.55) !important; }}

    /* ---- dark elevated panel/card ---- */
    .fl-card {{
        background: linear-gradient(155deg, var(--ember) 0%, var(--void2) 100%);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        box-shadow: 0 10px 26px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.03);
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    }}
    .fl-card:hover {{
        transform: translateY(-3px);
        border-color: rgba(255,106,26,0.4);
        box-shadow: 0 16px 34px rgba(0,0,0,0.35), 0 0 0 1px rgba(255,106,26,0.08);
    }}
    .fl-card h4 {{ color: var(--gold) !important; margin-top: 0; }}
    .fl-card b {{ color: var(--amber); }}

    /* ---- light panel/card, the lighter end of the palette ---- */
    .fl-card-light {{
        background: linear-gradient(155deg, var(--peach) 0%, var(--lightorange) 100%);
        border: 1px solid var(--gold);
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        color: var(--ink);
        box-shadow: 0 10px 26px rgba(0,0,0,0.22);
        transition: transform 0.22s ease, box-shadow 0.22s ease;
    }}
    .fl-card-light:hover {{
        transform: translateY(-3px);
        box-shadow: 0 16px 34px rgba(0,0,0,0.28);
    }}
    .fl-card-light h4 {{ color: var(--rust) !important; margin-top: 0; }}
    .fl-card-light p, .fl-card-light li {{ color: var(--ink); }}
    .fl-card-light b {{ color: var(--rust); }}

    /* ---- hero, now a two-column layout: text left, stat stack right ---- */
    .fl-hero {{
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 2.4rem 2.6rem;
        background:
            radial-gradient(circle at 8% 20%, rgba(255,179,71,0.18), transparent 55%),
            linear-gradient(135deg, var(--herostart) 0%, var(--heroend) 100%);
        margin-bottom: 1.8rem;
        position: relative; overflow: hidden;
        display: flex; gap: 2.5rem; align-items: center; flex-wrap: wrap;
        box-shadow: 0 16px 40px rgba(0,0,0,0.35);
    }}
    .fl-hero-text {{ flex: 1 1 420px; min-width: 300px; }}
    .fl-hero-stats {{ flex: 0 0 300px; display: flex; flex-direction: column; gap: 0.7rem; min-width: 260px; }}

    .fl-eyebrow {{
        font-family: 'JetBrains Mono', monospace; font-size: 0.74rem;
        letter-spacing: 0.24em; text-transform: uppercase; color: var(--gold);
    }}
    .fl-title {{
        font-family: 'Rajdhani', sans-serif; font-weight: 700;
        font-size: clamp(2.2rem, 3.4vw, 3.1rem);
        line-height: 1.05; margin: 0.35rem 0 0.7rem 0;
        background: linear-gradient(90deg, var(--cream), var(--gold));
        -webkit-background-clip: text; background-clip: text; color: transparent;
    }}
    .fl-sub {{ color: var(--creamdim); font-size: 0.96rem; max-width: 52ch; line-height: 1.55; }}

    /* ---- vertical stat cards inside the hero ---- */
    .fl-stat-v {{
        background: rgba(21,12,6,0.38);
        border: 1px solid rgba(255,201,92,0.22);
        border-radius: 14px;
        padding: 0.85rem 1.1rem;
        display: flex; align-items: center; gap: 0.9rem;
        backdrop-filter: blur(2px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .fl-stat-v:hover {{ transform: translateX(-3px); border-color: rgba(255,106,26,0.55); }}
    .fl-stat-v .icon {{
        width: 40px; height: 40px; border-radius: 12px; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center; font-size: 1.15rem;
    }}
    .fl-stat-v .num {{
        font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 1.55rem;
        color: var(--cream); line-height: 1.1;
    }}
    .fl-stat-v .lbl {{
        font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em;
        color: var(--creamdim); margin-top: 0.1rem;
    }}

    /* ---- generic horizontal stat chip row (used inside tabs) ---- */
    .fl-stat-row {{ display: flex; flex-wrap: wrap; gap: 0.7rem; margin-bottom: 0.3rem; }}
    .fl-stat {{
        background: linear-gradient(160deg, var(--ember2) 0%, var(--ember) 100%);
        border: 1px solid var(--line); border-radius: 12px;
        padding: 0.85rem 1.15rem; display: inline-flex; align-items: center; gap: 0.75rem;
        flex: 0 0 auto;
        box-shadow: 0 6px 16px rgba(0,0,0,0.22);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }}
    .fl-stat:hover {{ transform: translateY(-2px); box-shadow: 0 10px 22px rgba(0,0,0,0.3); }}
    .fl-stat .badge {{
        width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Rajdhani', sans-serif; font-weight: 700; color: #150B06;
        font-size: 1.0rem;
    }}
    .fl-stat .num {{
        font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 1.4rem;
        color: var(--gold); line-height: 1.1; white-space: nowrap;
    }}
    .fl-stat .lbl {{
        font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.09em;
        color: var(--creamdim); white-space: nowrap;
    }}

    /* ---- premium section divider ---- */
    .fl-divider {{ display: flex; align-items: center; gap: 12px; margin: 2rem 0 1.3rem 0; }}
    .fl-divider .ln {{ flex: 1; height: 1px; background: linear-gradient(90deg, var(--line), transparent); }}
    .fl-divider .dot {{ width: 10px; height: 10px; border-radius: 50%; box-shadow: 0 0 10px rgba(255,106,26,0.7); }}
    .fl-divider .label {{
        font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 0.82rem; color: var(--cream);
        letter-spacing: 0.16em; text-transform: uppercase; white-space: nowrap;
    }}

    /* ---- player profile ---- */
    .fl-player-name {{
        font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 2.2rem;
        color: var(--cream); margin-bottom: 0.4rem;
    }}
    .fl-player-cat {{
        display: inline-block; padding: 0.18rem 0.75rem; border-radius: 20px;
        background: linear-gradient(135deg, var(--blaze), var(--rust));
        color: #150B06; font-family: 'Rajdhani', sans-serif; font-weight: 700;
        font-size: 0.78rem; letter-spacing: 0.06em; text-transform: uppercase;
        box-shadow: 0 4px 12px rgba(255,106,26,0.3);
    }}

    /* ---- insight cards, alternating dark / light surfaces ---- */
    .fl-insight {{
        background: linear-gradient(155deg, var(--ember) 0%, var(--void2) 100%);
        border-radius: 12px; padding: 1rem 1.15rem 1rem 1.05rem; margin-bottom: 0.75rem;
        display: flex; gap: 0.75rem; align-items: flex-start;
        box-shadow: 0 6px 16px rgba(0,0,0,0.22);
        transition: transform 0.18s ease;
    }}
    .fl-insight:hover {{ transform: translateX(3px); }}
    .fl-insight .ic {{ font-size: 1.25rem; line-height: 1.3; }}
    .fl-insight b {{ color: var(--gold); }}
    .fl-insight-light {{
        background: linear-gradient(155deg, var(--peach) 0%, var(--lightorange) 100%);
        border-radius: 12px; padding: 1rem 1.15rem 1rem 1.05rem; margin-bottom: 0.75rem;
        display: flex; gap: 0.75rem; align-items: flex-start; color: var(--ink);
        box-shadow: 0 6px 16px rgba(0,0,0,0.18);
        transition: transform 0.18s ease;
    }}
    .fl-insight-light:hover {{ transform: translateX(3px); }}
    .fl-insight-light .ic {{ font-size: 1.25rem; line-height: 1.3; }}
    .fl-insight-light b {{ color: var(--rust); }}
    .fl-insight-light div {{ color: var(--ink); }}

    /* ---- custom orange tables (replaces default blue dataframe grid) ---- */
    .fl-table-wrap {{ border: 1px solid var(--line); border-radius: 12px; overflow: auto; margin-bottom: 0.7rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.22); }}
    table.fl-table {{ width: 100%; border-collapse: collapse; font-size: 0.84rem; }}
    table.fl-table thead th {{
        position: sticky; top: 0;
        background: linear-gradient(135deg, var(--rust), var(--blaze));
        color: #150B06; padding: 0.6rem 0.9rem; text-align: left;
        font-family: 'Rajdhani', sans-serif; font-weight: 700; letter-spacing: 0.03em;
        text-transform: uppercase; font-size: 0.7rem; white-space: nowrap;
    }}
    table.fl-table tbody td {{
        padding: 0.5rem 0.9rem; border-bottom: 1px solid var(--line);
        color: var(--cream); white-space: nowrap;
    }}
    table.fl-table tbody tr:nth-child(odd) {{ background: var(--void2); }}
    table.fl-table tbody tr:nth-child(even) {{ background: var(--ember); }}
    table.fl-table tbody tr:hover {{ background: var(--ember2); }}

    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: var(--void2); }}
    ::-webkit-scrollbar-thumb {{ background: var(--rust); border-radius: 6px; }}

    @media (max-width: 900px) {{
        .fl-hero {{ flex-direction: column; align-items: stretch; }}
        .fl-hero-stats {{ flex: 1 1 auto; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def pitch_divider(label: str, accent: str = BLAZE):
    st.markdown(
        f"""<div class="fl-divider"><div class="dot" style="border:2px solid {accent};"></div>
        <div class="ln"></div><div class="label">{label}</div><div class="ln"></div></div>""",
        unsafe_allow_html=True,
    )


def stat_chip_row(chips):
    """chips: list of (badge_text, value, label, accent_color) — horizontal row, used inside tabs."""
    html = ['<div class="fl-stat-row">']
    for badge, value, label, accent in chips:
        html.append(
            f"""<div class="fl-stat"><div class="badge" style="background:{accent};">{badge}</div>
            <div><div class="num">{value}</div><div class="lbl">{label}</div></div></div>"""
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def hero_stat_card(icon, value, label, accent):
    return f"""<div class="fl-stat-v">
        <div class="icon" style="background:{accent};">{icon}</div>
        <div><div class="num">{value}</div><div class="lbl">{label}</div></div>
        </div>"""


def render_table(df, index=True, height=360):
    """Render a DataFrame as a custom-styled orange HTML table (no default blue grid)."""
    styled = df.copy()
    for col in styled.select_dtypes(include=["float", "float64"]).columns:
        styled[col] = styled[col].round(2)
    html = styled.to_html(index=index, border=0, classes="fl-table", escape=True)
    style = f"max-height:{height}px;" if height else ""
    st.markdown(f'<div class="fl-table-wrap" style="{style}">{html}</div>', unsafe_allow_html=True)


# ============================================================================
# 3. MATPLOTLIB THEME
# ============================================================================
def style_axes(fig, axes):
    fig.patch.set_facecolor(VOID_2)
    if not isinstance(axes, (list, np.ndarray)):
        axes = [axes]
    for ax in np.ravel(axes):
        ax.set_facecolor(VOID)
        ax.tick_params(colors=CREAM_DIM, labelsize=9)
        ax.xaxis.label.set_color(CREAM)
        ax.yaxis.label.set_color(CREAM)
        ax.title.set_color(GOLD)
        for spine in ax.spines.values():
            spine.set_color(LINE)
        ax.grid(color=LINE, alpha=0.45, linewidth=0.6)
        ax.set_axisbelow(True)


def gradient_bars(values):
    n = max(len(values), 1)
    order = np.argsort(np.argsort(-np.array(values)))
    return [ORANGE_CMAP(1 - (r / max(n - 1, 1)) * 0.75) for r in order]


def chart_top_n_bar(df, column, n=10, title=None, figsize=(6.4, 4.5)):
    top_df = df.sort_values(column, ascending=False).head(n)
    fig, ax = plt.subplots(figsize=figsize)
    colors = gradient_bars(top_df[column].values)
    ax.bar(top_df["Player"], top_df[column], color=colors, edgecolor=VOID_2, linewidth=0.6)
    ax.set_title(title or f"Top {n} by {column}", fontsize=12)
    ax.set_ylabel(column)
    plt.setp(ax.get_xticklabels(), rotation=42, ha="right", fontsize=8)
    style_axes(fig, ax)
    fig.tight_layout()
    return fig


def chart_histogram(df, column, bins=12, log_scale=False, figsize=(6.4, 4.3)):
    fig, ax = plt.subplots(figsize=figsize)
    counts, edges, patches = ax.hist(df[column].dropna(), bins=bins, edgecolor=VOID_2, linewidth=0.6)
    for i, p in enumerate(patches):
        p.set_facecolor(ORANGE_CMAP(0.25 + 0.7 * (i / max(len(patches) - 1, 1))))
    if log_scale:
        ax.set_yscale("log")
    ax.set_title(f"{column} Distribution" + (" (log scale)" if log_scale else ""), fontsize=12)
    ax.set_xlabel(column)
    ax.set_ylabel("Players")
    style_axes(fig, ax)
    fig.tight_layout()
    return fig


def chart_boxplot(df, column, figsize=(6.4, 4.3)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.boxplot(
        df[column].dropna(), patch_artist=True, widths=0.4,
        boxprops=dict(facecolor=AMBER, color=LINE),
        medianprops=dict(color=VOID, linewidth=2),
        whiskerprops=dict(color=CREAM_DIM), capprops=dict(color=CREAM_DIM),
        flierprops=dict(markerfacecolor=BLAZE, markeredgecolor=RUST, markersize=5, alpha=0.7),
    )
    ax.set_title(f"{column} Spread", fontsize=12)
    ax.set_xticks([])
    style_axes(fig, ax)
    fig.tight_layout()
    return fig


def chart_category_counts(df, figsize=(6.4, 4.3)):
    counts = df["Category"].value_counts()
    fig, ax = plt.subplots(figsize=figsize)
    colors = [ORANGE_CMAP(0.2 + 0.7 * i / max(len(counts) - 1, 1)) for i in range(len(counts))]
    ax.bar(counts.index, counts.values, color=colors, edgecolor=VOID_2, linewidth=0.6)
    ax.set_title("Players by Category", fontsize=12)
    ax.set_ylabel("Players")
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right", fontsize=8)
    style_axes(fig, ax)
    fig.tight_layout()
    return fig


def chart_average_by_category(df, column, figsize=(6.4, 4.3)):
    avg = df.groupby("Category")[column].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=figsize)
    colors = gradient_bars(avg.values)
    ax.bar(avg.index, avg.values, color=colors, edgecolor=VOID_2, linewidth=0.6)
    ax.set_title(f"Average {column} by Category", fontsize=12)
    ax.set_ylabel(f"Avg. {column}")
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right", fontsize=8)
    style_axes(fig, ax)
    fig.tight_layout()
    return fig


def chart_scatter(df, x_col, y_col, figsize=(6.4, 4.5)):
    fig, ax = plt.subplots(figsize=figsize)
    vals = df[y_col].values
    order = np.argsort(vals)
    ranks = np.argsort(order) / max(len(vals) - 1, 1)
    colors = [ORANGE_CMAP(0.25 + 0.65 * r) for r in ranks]
    ax.scatter(df[x_col], df[y_col], c=colors, s=40, edgecolor=VOID_2, linewidth=0.4, alpha=0.9)
    ax.set_title(f"{x_col} vs {y_col}", fontsize=12)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    style_axes(fig, ax)
    fig.tight_layout()
    return fig


def chart_correlation_heatmap(df, columns, figsize=(6.6, 5.6)):
    corr = df[columns].corr()
    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(corr.values, cmap=ORANGE_CMAP, vmin=-1, vmax=1)
    ax.set_xticks(range(len(columns)))
    ax.set_yticks(range(len(columns)))
    ax.set_xticklabels(columns, rotation=45, ha="right", fontsize=7.5, color=CREAM_DIM)
    ax.set_yticklabels(columns, fontsize=7.5, color=CREAM_DIM)
    for i in range(len(columns)):
        for j in range(len(columns)):
            val = corr.values[i, j]
            txt_color = VOID if val > 0.35 else CREAM
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=txt_color, fontsize=7)
    ax.set_title("Correlation Between Key Stats", fontsize=12, color=GOLD)
    fig.patch.set_facecolor(VOID_2)
    for spine in ax.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
    cbar.ax.yaxis.set_tick_params(color=CREAM_DIM, labelcolor=CREAM_DIM)
    fig.tight_layout()
    return fig


def chart_player_compare(compare_df, figsize=(9.5, 5)):
    fig, ax = plt.subplots(figsize=figsize)
    n_players = len(compare_df.columns)
    n_stats = len(compare_df.index)
    width = 0.8 / max(n_players, 1)
    x = np.arange(n_stats)
    palette = [ORANGE_CMAP(0.15 + 0.75 * i / max(n_players - 1, 1)) for i in range(n_players)]
    for i, player in enumerate(compare_df.columns):
        ax.bar(x + i * width, compare_df[player].values, width=width, label=player,
               color=palette[i], edgecolor=VOID_2, linewidth=0.5)
    ax.set_xticks(x + width * (n_players - 1) / 2)
    ax.set_xticklabels(compare_df.index, rotation=30, ha="right")
    ax.set_title("Player Comparison", fontsize=12)
    ax.legend(facecolor=EMBER, edgecolor=LINE, labelcolor=CREAM, fontsize=9)
    style_axes(fig, ax)
    fig.tight_layout()
    return fig


# ============================================================================
# 4. DATA LOADING
# ============================================================================
@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def get_numeric_columns(df: pd.DataFrame) -> list:
    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    drop = {"level_1", "Rank"}
    return [c for c in numeric if c not in drop]


try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.markdown(
        f"""<div class="fl-card"><h3>Dataset not found</h3>
        <p class="fl-sub">Could not locate <code>{DATA_PATH}</code>.
        Run <code>cleaning/clean_data.py</code> first to generate
        <code>data/players_cleaned.csv</code>.</p></div>""",
        unsafe_allow_html=True,
    )
    st.stop()

numeric_columns = get_numeric_columns(df)
available_key_stats = [c for c in KEY_STATS if c in df.columns]

# ============================================================================
# 5. SIDEBAR — logo, navigation, then filters ("team sheet")
# ============================================================================
st.sidebar.markdown(
    """<div class="fl-logo">
        <div class="ball">⚽</div>
        <div>
            <div class="txt-main">FIFA 2026</div>
            <div class="txt-sub">Player Analysis</div>
        </div>
    </div>""",
    unsafe_allow_html=True,
)

st.sidebar.markdown('<div class="fl-side-heading">Navigation</div>', unsafe_allow_html=True)
nav_options = ["🏠 Home", "🔍 Player Explorer", "⚖️ Compare", "📊 Statistics", "💡 Insights"]
nav_selection = st.sidebar.radio(
    "Navigation", options=nav_options, label_visibility="collapsed", key="fl_nav"
)

st.sidebar.markdown('<hr class="fl-side-divider">', unsafe_allow_html=True)
st.sidebar.markdown('<div class="fl-side-heading">Team Sheet</div>', unsafe_allow_html=True)
st.sidebar.caption("Filters apply to every tab")

categories = sorted(df["Category"].dropna().unique().tolist()) if "Category" in df.columns else []
selected_categories = st.sidebar.multiselect("Category", options=categories, default=categories)

search_term = st.sidebar.text_input("Search player", placeholder="e.g. Mbappé")

involvement_col = "Player Involvements" if "Player Involvements" in df.columns else None
min_involvement = 0
if involvement_col:
    max_inv = int(df[involvement_col].max())
    min_involvement = st.sidebar.slider(
        "Min. player involvements", 0, max(max_inv, 1), 0,
        help="Filters out players with very few recorded touches/involvements.",
    )

range_col = None
range_bounds = None
if numeric_columns:
    range_col = st.sidebar.selectbox("Fine-tune by stat", options=["(none)"] + numeric_columns)
    if range_col != "(none)":
        lo, hi = float(df[range_col].min()), float(df[range_col].max())
        if lo < hi:
            range_bounds = st.sidebar.slider(f"{range_col} range", lo, hi, (lo, hi))

filtered_df = df[df["Category"].isin(selected_categories)] if selected_categories else df.copy()
if involvement_col:
    filtered_df = filtered_df[filtered_df[involvement_col] >= min_involvement]
if search_term:
    filtered_df = filtered_df[filtered_df["Player"].str.contains(search_term, case=False, na=False)]
if range_col and range_col != "(none)" and range_bounds:
    filtered_df = filtered_df[
        (filtered_df[range_col] >= range_bounds[0]) & (filtered_df[range_col] <= range_bounds[1])
    ]

st.sidebar.markdown('<hr class="fl-side-divider">', unsafe_allow_html=True)
st.sidebar.markdown(
    f"""<div class="fl-card"><div class="fl-eyebrow" style="color:{AMBER};">IN VIEW</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:1.8rem;font-weight:700;color:{GOLD};">
    {len(filtered_df)}</div><div style="font-size:0.75rem;color:{CREAM_DIM};">
    of {len(df)} players</div></div>""",
    unsafe_allow_html=True,
)

st.sidebar.markdown('<hr class="fl-side-divider">', unsafe_allow_html=True)
st.sidebar.download_button(
    "⬇ Download filtered CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="fifa2026_filtered_players.csv",
    mime="text/csv",
    use_container_width=True,
)

if filtered_df.empty:
    st.warning("No players match the current filters. Adjust the team sheet in the sidebar.")
    st.stop()

# ============================================================================
# 6. MAIN CONTENT — driven by the sidebar navigation selection
# ============================================================================

# ---- HOME -------------------------------------------------------------
if nav_selection == "🏠 Home":
    # Hero — two-column layout: text on the left, stacked stat cards on the
    # right. Lives on Home only, so the other tabs get straight to their content.
    hero_chips = [("⚽", f"{len(filtered_df):,}", "Players in view", BLAZE)]
    if "Category" in filtered_df.columns:
        hero_chips.append(("🗂️", filtered_df["Category"].nunique(), "Categories", AMBER))
    if "Goal Contribution" in filtered_df.columns:
        avg_gc = filtered_df["Goal Contribution"].mean()
        top_row = filtered_df.loc[filtered_df["Goal Contribution"].idxmax()]
        hero_chips.append(("🎯", f"{avg_gc:.1f}", "Avg. goal contribution", GOLD))
        hero_chips.append(("🏆", top_row["Player"], f"Top contributor · {top_row['Goal Contribution']:.0f}", RUST))

    hero_stats_html = "".join(hero_stat_card(icon, value, label, accent) for icon, value, label, accent in hero_chips)

    st.markdown(
        f"""
        <div class="fl-hero">
            <div class="fl-hero-text">
                <div class="fl-eyebrow">PLAYER STATISTICS</div>
                <div class="fl-title">FIFA World Cup 2026<br>Player Analysis</div>
                <div class="fl-sub">Scraped from fifa.com, cleaned, and broken down across eight
                performance categories: attacking, distribution, defending, discipline,
                goalkeeping, movement and physical output. Explore rankings, distributions,
                correlations, and individual player profiles using the sidebar.</div>
            </div>
            <div class="fl-hero-stats">{hero_stats_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pitch_divider("About This Project", ACCENTS[0])
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """<div class="fl-card">
            <h4>What this dashboard covers</h4>
            <p>Every player row here was pulled from FIFA's official World Cup 2026
            statistics pages, one performance category at a time, then combined,
            cleaned, and rebuilt into a single table. Categories include attacking,
            distribution, defending, discipline, goalkeeping, movement, and
            physical output, so a defender and a striker are judged on genuinely
            different scales rather than one generic scoreboard.</p>
            <p>Use the sidebar to move between an overview, a searchable player
            profile, a head to head comparison tool, a full statistics workbench,
            and a set of auto-generated findings that update as you filter.</p>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """<div class="fl-card-light">
            <h4>Reading the key metrics</h4>
            <ul style="margin:0; padding-left:1.1rem;">
            <li><b>Goal Contribution</b> combines assists and attempts at goal
            into one attacking output score.</li>
            <li><b>Goal Efficiency</b> is assists divided by attempts, a rough
            read on how well an attempt turns into a real chance.</li>
            <li><b>xG Efficiency</b> compares actual output against the
            expected goal value of a player's chances.</li>
            <li><b>Player Involvements</b> counts total touches and actions
            recorded across a match.</li>
            </ul></div>""",
            unsafe_allow_html=True,
        )

    pitch_divider("Data Preview", ACCENTS[1])
    render_table(filtered_df.head(25), index=False, height=360)

    with st.expander("Full descriptive statistics"):
        stats = summary_stats(filtered_df)
        render_table(stats["describe"], index=True, height=360)

# ---- PLAYER EXPLORER ----------------------------------------------------
elif nav_selection == "🔍 Player Explorer":
    pitch_divider("Player Profile", ACCENTS[0])
    player_options = sorted(filtered_df["Player"].dropna().unique().tolist())
    if not player_options:
        st.info("No players available with the current filters.")
    else:
        selected_player = st.selectbox("Select a player", options=player_options)
        row = filtered_df[filtered_df["Player"] == selected_player].iloc[0]

        cat_html = f'<span class="fl-player-cat">{row["Category"]}</span>' if "Category" in row else ""
        st.markdown(
            f"""<div class="fl-card" style="margin-bottom:1rem;">
            <div class="fl-player-name">{selected_player}</div>{cat_html}</div>""",
            unsafe_allow_html=True,
        )

        chips = []
        for i, col in enumerate(available_key_stats[:8]):
            val = row.get(col, np.nan)
            display_val = f"{val:.2f}" if isinstance(val, (int, float, np.floating)) else str(val)
            chips.append((f"{i+1:02d}", display_val, col, ACCENTS[i % len(ACCENTS)]))
        stat_chip_row(chips)

        pitch_divider("Full Stat Line", ACCENTS[2])
        display_cols = [c for c in numeric_columns if c != "Rank"]
        render_table(row[display_cols].to_frame(name="Value"), index=True, height=360)

# ---- COMPARE ------------------------------------------------------------
elif nav_selection == "⚖️ Compare":
    pitch_divider("Head to Head", ACCENTS[0])
    player_options = sorted(filtered_df["Player"].dropna().unique().tolist())
    compare_players = st.multiselect(
        "Players to compare (up to 4)", options=player_options,
        default=player_options[:2] if len(player_options) >= 2 else player_options,
        max_selections=4,
    )
    compare_stats = st.multiselect(
        "Stats to compare", options=available_key_stats,
        default=[c for c in ["Assists", "Attempts At Goal", "Passes", "Goal Contribution"] if c in available_key_stats],
    )

    if compare_players and compare_stats:
        compare_df = filtered_df[filtered_df["Player"].isin(compare_players)].set_index("Player")[compare_stats].T
        fig = chart_player_compare(compare_df)
        st.pyplot(fig)
        plt.close(fig)
        render_table(compare_df, index=True, height=320)
    else:
        st.info("Pick at least one player and one stat to compare.")

# ---- STATISTICS -----------------------------------------------------------
elif nav_selection == "📊 Statistics":
    pitch_divider("Squad Composition", ACCENTS[0])
    col1, col2 = st.columns(2)
    with col1:
        if "Category" in filtered_df.columns:
            fig = chart_category_counts(filtered_df)
            st.pyplot(fig)
            plt.close(fig)
    with col2:
        if "Category" in filtered_df.columns and numeric_columns:
            comp_default = "Goal Contribution" if "Goal Contribution" in numeric_columns else numeric_columns[0]
            comp_col = st.selectbox("Average metric by category", options=numeric_columns,
                                     index=numeric_columns.index(comp_default))
            fig = chart_average_by_category(filtered_df, comp_col)
            st.pyplot(fig)
            plt.close(fig)

    pitch_divider("Rankings", ACCENTS[1])
    default_stat = "Goal Contribution" if "Goal Contribution" in numeric_columns else numeric_columns[0]
    ctrl_a, ctrl_b = st.columns([2, 1])
    with ctrl_a:
        rank_column = st.selectbox("Stat to rank by", options=numeric_columns, index=numeric_columns.index(default_stat))
    with ctrl_b:
        top_n_value = st.slider("Number of players", 5, 25, 10)

    col1, col2 = st.columns(2)
    with col1:
        fig = chart_top_n_bar(filtered_df, rank_column, n=top_n_value)
        st.pyplot(fig)
        plt.close(fig)
    with col2:
        render_table(top_n(filtered_df, rank_column, n=top_n_value), index=False, height=420)

    pitch_divider("Distribution", ACCENTS[2])
    default_dist = "Attempts At Goal" if "Attempts At Goal" in numeric_columns else numeric_columns[0]
    ctrl_c, ctrl_d, ctrl_e = st.columns([2, 1, 1])
    with ctrl_c:
        dist_column = st.selectbox("Stat", options=numeric_columns, index=numeric_columns.index(default_dist), key="dist_col")
    with ctrl_d:
        bins = st.slider("Bins", 5, 40, 12)
    with ctrl_e:
        log_scale = st.checkbox("Log scale", value=False)

    col1, col2 = st.columns(2)
    with col1:
        fig = chart_histogram(filtered_df, dist_column, bins=bins, log_scale=log_scale)
        st.pyplot(fig)
        plt.close(fig)
    with col2:
        fig = chart_boxplot(filtered_df, dist_column)
        st.pyplot(fig)
        plt.close(fig)

    stats = summary_stats(filtered_df)
    summary_table = pd.DataFrame({
        "Mean": [stats["mean"].get(dist_column, np.nan)],
        "Median": [stats["median"].get(dist_column, np.nan)],
        "Std Dev": [stats["std"].get(dist_column, np.nan)],
        "Variance": [stats["var"].get(dist_column, np.nan)],
        "Min": [stats["min"].get(dist_column, np.nan)],
        "Max": [stats["max"].get(dist_column, np.nan)],
    })
    render_table(summary_table, index=False, height=None)

    pitch_divider("Correlations & Relationships", ACCENTS[3])
    corr_columns = st.multiselect(
        "Columns in heatmap", options=numeric_columns,
        default=[c for c in available_key_stats if c in numeric_columns][:8] or numeric_columns[:6],
    )
    x_default = "Top Speed (km/h)" if "Top Speed (km/h)" in numeric_columns else numeric_columns[0]
    y_default = "Goal Contribution" if "Goal Contribution" in numeric_columns else numeric_columns[-1]
    ctrl_x, ctrl_y = st.columns(2)
    with ctrl_x:
        x_col = st.selectbox("X-axis", options=numeric_columns, index=numeric_columns.index(x_default))
    with ctrl_y:
        y_col = st.selectbox("Y-axis", options=numeric_columns, index=numeric_columns.index(y_default))

    col1, col2 = st.columns(2)
    with col1:
        if len(corr_columns) >= 2:
            fig = chart_correlation_heatmap(filtered_df, corr_columns)
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("Select at least two columns to build a heatmap.")
    with col2:
        fig = chart_scatter(filtered_df, x_col, y_col)
        st.pyplot(fig)
        plt.close(fig)

# ---- INSIGHTS ---------------------------------------------------------
elif nav_selection == "💡 Insights":
    pitch_divider("Key Findings", ACCENTS[0])

    icons = ["🏆", "⚡", "🎯", "🎯", "🏃", "🥇", "👥", "📈", "🧮", "🧭"]
    insights = []

    if "Category" in filtered_df.columns and "Goal Contribution" in filtered_df.columns:
        grp = filtered_df.groupby("Category")["Goal Contribution"].mean()
        insights.append(f"<b>{grp.idxmax()}</b> leads all categories with the highest average goal contribution, at <b>{grp.max():.2f}</b> per player.")

    if "Top Speed (km/h)" in filtered_df.columns and "Goal Contribution" in filtered_df.columns:
        corr = filtered_df["Top Speed (km/h)"].corr(filtered_df["Goal Contribution"])
        strength = "a strong" if abs(corr) > 0.5 else "a weak" if abs(corr) < 0.2 else "a moderate"
        direction = "positive" if corr > 0 else "negative"
        insights.append(f"Top speed and goal contribution show {strength} {direction} relationship, r equals <b>{corr:.2f}</b>.")

    if "Goal Efficiency" in filtered_df.columns and "Attempts At Goal" in filtered_df.columns:
        qualified = filtered_df[filtered_df["Attempts At Goal"] >= filtered_df["Attempts At Goal"].median()]
        if not qualified.empty:
            best = qualified.loc[qualified["Goal Efficiency"].idxmax()]
            insights.append(f"Among players with at least median shot volume, <b>{best['Player']}</b> converts most efficiently, at <b>{best['Goal Efficiency']:.2f}</b>.")

    if "Passing Accuracy (%)" in filtered_df.columns:
        top_passer = filtered_df.loc[filtered_df["Passing Accuracy (%)"].idxmax()]
        insights.append(f"<b>{top_passer['Player']}</b> posts the highest passing accuracy in view, at <b>{top_passer['Passing Accuracy (%)']:.1f}%</b>.")

    if "Top Speed (km/h)" in filtered_df.columns:
        fastest = filtered_df.loc[filtered_df["Top Speed (km/h)"].idxmax()]
        insights.append(f"<b>{fastest['Player']}</b> is the fastest player in view, clocked at <b>{fastest['Top Speed (km/h)']:.1f} km/h</b>.")

    if "Total Distance (m)" in filtered_df.columns:
        avg_dist = filtered_df["Total Distance (m)"].mean()
        insights.append(f"Players in view cover an average of <b>{avg_dist:,.0f}m</b> per match on record.")

    if "Category" in filtered_df.columns:
        biggest_cat = filtered_df["Category"].value_counts().idxmax()
        insights.append(f"<b>{biggest_cat}</b> is the most populated category currently in view.")

    if "Passes" in filtered_df.columns:
        top_passer_vol = filtered_df.loc[filtered_df["Passes"].idxmax()]
        insights.append(f"<b>{top_passer_vol['Player']}</b> has completed the most passes in view, at <b>{top_passer_vol['Passes']:.0f}</b>.")

    if "Goal Efficiency" in filtered_df.columns:
        insights.append(f"The average goal efficiency across all players in view sits at <b>{filtered_df['Goal Efficiency'].mean():.2f}</b>.")

    if "Passing Accuracy (%)" in filtered_df.columns and "Category" in filtered_df.columns:
        best_passing_cat = filtered_df.groupby("Category")["Passing Accuracy (%)"].mean().idxmax()
        insights.append(f"<b>{best_passing_cat}</b> holds the best average passing accuracy among all categories.")

    if not insights:
        insights.append("Not enough numeric columns available in this dataset view to generate insights.")

    for i, text in enumerate(insights):
        accent = ACCENTS[i % len(ACCENTS)]
        icon = icons[i % len(icons)]
        card_class = "fl-insight" if i % 2 == 0 else "fl-insight-light"
        st.markdown(
            f"""<div class="{card_class}" style="border-left:3px solid {accent};">
            <div class="ic">{icon}</div><div>{text}</div></div>""",
            unsafe_allow_html=True,
        )

st.markdown(
    """<div style="text-align:center;color:#C99A6E;font-size:0.75rem;
    letter-spacing:0.08em;text-transform:uppercase;margin-top:2.4rem;">
    Built with Pandas · NumPy · Matplotlib · Streamlit</div>""",
    unsafe_allow_html=True,
)