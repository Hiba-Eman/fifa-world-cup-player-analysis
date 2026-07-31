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
    # Fallback so the dashboard still runs if the package import path differs
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
# 1. PALETTE — one warm-orange family, nothing else
# ============================================================================
VOID = "#120A06"        # page background — near-black, warm charcoal-ember
VOID_2 = "#1B0F08"       # secondary background
EMBER = "#26150C"        # card surface
EMBER_2 = "#341C10"      # card surface, hover / raised
LINE = "#4A2A15"         # hairlines, gridlines, borders
RUST = "#B8420E"         # deep accent
BLAZE = "#FF5E1A"        # primary accent
AMBER = "#FFA33E"        # secondary accent
GOLD = "#FFC971"         # tertiary accent
CREAM = "#FFE7C2"        # primary text
CREAM_DIM = "#C99A6E"    # secondary / muted text

ORANGE_CMAP = LinearSegmentedColormap.from_list(
    "floodlight", [RUST, BLAZE, AMBER, GOLD]
)

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
        --void: {VOID}; --void2: {VOID_2}; --ember: {EMBER}; --ember2: {EMBER_2};
        --line: {LINE}; --rust: {RUST}; --blaze: {BLAZE}; --amber: {AMBER};
        --gold: {GOLD}; --cream: {CREAM}; --creamdim: {CREAM_DIM};
    }}

    html, body, [class*="css"] {{ font-family: 'Manrope', sans-serif; }}

    .stApp {{
        background:
            radial-gradient(ellipse 900px 500px at 15% -8%, rgba(255,94,26,0.16), transparent 60%),
            radial-gradient(ellipse 700px 500px at 100% 10%, rgba(255,163,62,0.10), transparent 55%),
            var(--void);
        color: var(--cream);
    }}

    /* ---- kill default streamlit chrome ---- */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1400px; }}

    /* ---- headings ---- */
    h1, h2, h3, h4 {{
        font-family: 'Rajdhani', sans-serif !important;
        color: var(--cream) !important;
        letter-spacing: 0.02em;
        font-weight: 700 !important;
    }}
    p, span, label, div {{ color: var(--cream); }}

    /* ---- sidebar: "team sheet" panel ---- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, var(--void2) 0%, var(--ember) 100%);
        border-right: 1px solid var(--line);
    }}
    section[data-testid="stSidebar"] .block-container {{ padding-top: 1.4rem; }}

    /* ---- tabs styled like a scoreboard strip ---- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px; border-bottom: 1px solid var(--line); background: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 44px; background: var(--ember); border-radius: 8px 8px 0 0;
        color: var(--creamdim) !important; font-family: 'Rajdhani', sans-serif;
        font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
        font-size: 0.85rem; padding: 0 18px; border: 1px solid var(--line);
        border-bottom: none;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(180deg, var(--blaze), var(--rust)) !important;
        color: #150B06 !important;
        box-shadow: 0 -6px 18px rgba(255,94,26,0.35);
    }}

    /* ---- buttons / inputs ---- */
    .stButton>button, .stDownloadButton>button {{
        background: linear-gradient(135deg, var(--blaze), var(--rust));
        color: #150B06; border: none; border-radius: 8px; font-weight: 700;
        font-family: 'Rajdhani', sans-serif; letter-spacing: 0.04em;
        text-transform: uppercase; padding: 0.55rem 1.1rem;
        box-shadow: 0 4px 14px rgba(255,94,26,0.25);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .stButton>button:hover, .stDownloadButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(255,94,26,0.45);
        color: #150B06;
    }}

    div[data-baseweb="select"] > div, .stTextInput input, .stMultiSelect div[data-baseweb="select"] {{
        background-color: var(--ember) !important;
        border: 1px solid var(--line) !important;
        color: var(--cream) !important;
        border-radius: 8px !important;
    }}
    .stSlider [data-baseweb="slider"] div {{ background: var(--line); }}
    .stSlider [role="slider"] {{ background: var(--blaze) !important; border-color: var(--blaze) !important; }}

    /* ---- generic panel/card ---- */
    .fl-card {{
        background: linear-gradient(155deg, var(--ember) 0%, var(--void2) 100%);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
    }}

    /* ---- hero ---- */
    .fl-hero {{
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 2.2rem 2.4rem;
        background:
            radial-gradient(circle at 8% 20%, rgba(255,163,62,0.16), transparent 55%),
            linear-gradient(135deg, var(--ember) 0%, var(--void2) 100%);
        margin-bottom: 1.6rem;
        position: relative; overflow: hidden;
    }}
    .fl-eyebrow {{
        font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
        letter-spacing: 0.22em; text-transform: uppercase; color: var(--gold);
    }}
    .fl-title {{
        font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 2.6rem;
        line-height: 1.05; margin: 0.3rem 0 0.6rem 0;
        background: linear-gradient(90deg, var(--cream), var(--gold));
        -webkit-background-clip: text; background-clip: text; color: transparent;
    }}
    .fl-sub {{ color: var(--creamdim); font-size: 0.98rem; max-width: 62ch; }}

    /* ---- stat cards ---- */
    .fl-stat {{
        background: linear-gradient(160deg, var(--ember2) 0%, var(--ember) 100%);
        border: 1px solid var(--line); border-radius: 12px;
        padding: 0.95rem 1.1rem; display: flex; align-items: center; gap: 0.8rem;
        height: 100%;
    }}
    .fl-stat .badge {{
        width: 38px; height: 38px; border-radius: 50%; flex-shrink: 0;
        background: linear-gradient(135deg, var(--blaze), var(--rust));
        display: flex; align-items: center; justify-content: center;
        font-family: 'Rajdhani', sans-serif; font-weight: 700; color: #150B06;
        font-size: 1.05rem;
    }}
    .fl-stat .num {{
        font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 1.55rem;
        color: var(--gold); line-height: 1;
    }}
    .fl-stat .lbl {{
        font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em;
        color: var(--creamdim);
    }}

    /* ---- pitch divider (halfway line motif) ---- */
    .fl-divider {{
        display: flex; align-items: center; gap: 12px; margin: 1.6rem 0 1.2rem 0;
    }}
    .fl-divider .ln {{ flex: 1; height: 1px; background: var(--line); }}
    .fl-divider .dot {{
        width: 10px; height: 10px; border-radius: 50%; border: 2px solid var(--blaze);
    }}
    .fl-divider .label {{
        font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--creamdim);
        letter-spacing: 0.15em; text-transform: uppercase;
    }}

    /* ---- rank badges in tables ---- */
    .fl-rank {{
        display: inline-flex; align-items: center; justify-content: center;
        width: 26px; height: 26px; border-radius: 6px; margin-right: 8px;
        background: var(--ember2); border: 1px solid var(--line);
        font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--gold);
    }}

    /* ---- player profile card ---- */
    .fl-player-name {{
        font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 2.1rem;
        color: var(--cream); margin-bottom: 0;
    }}
    .fl-player-cat {{
        display: inline-block; padding: 0.15rem 0.7rem; border-radius: 20px;
        background: linear-gradient(135deg, var(--blaze), var(--rust));
        color: #150B06; font-family: 'Rajdhani', sans-serif; font-weight: 700;
        font-size: 0.78rem; letter-spacing: 0.06em; text-transform: uppercase;
    }}

    /* ---- insight card ---- */
    .fl-insight {{
        background: linear-gradient(155deg, var(--ember) 0%, var(--void2) 100%);
        border-left: 3px solid var(--blaze); border-radius: 8px;
        padding: 0.9rem 1.1rem; margin-bottom: 0.7rem;
    }}
    .fl-insight b {{ color: var(--gold); }}

    /* dataframe wrapper */
    [data-testid="stDataFrame"] {{
        border: 1px solid var(--line); border-radius: 10px; overflow: hidden;
    }}

    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: var(--void2); }}
    ::-webkit-scrollbar-thumb {{ background: var(--rust); border-radius: 6px; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def pitch_divider(label: str):
    st.markdown(
        f"""<div class="fl-divider"><div class="dot"></div><div class="ln"></div>
        <div class="label">{label}</div><div class="ln"></div></div>""",
        unsafe_allow_html=True,
    )


def stat_card(col, badge, num, label):
    with col:
        st.markdown(
            f"""<div class="fl-stat"><div class="badge">{badge}</div>
            <div><div class="num">{num}</div><div class="lbl">{label}</div></div></div>""",
            unsafe_allow_html=True,
        )


# ============================================================================
# 3. MATPLOTLIB THEME — every chart drawn in the same orange family
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
        ax.grid(color=LINE, alpha=0.55, linewidth=0.6)
        ax.set_axisbelow(True)


def gradient_bars(ax, values):
    """Assign each bar a color sampled from the floodlight colormap by rank."""
    n = max(len(values), 1)
    order = np.argsort(np.argsort(-np.array(values)))  # rank 0 = highest value
    colors = [ORANGE_CMAP(1 - (r / max(n - 1, 1)) * 0.75) for r in order]
    return colors


def chart_top_n_bar(df, column, n=10, title=None):
    top_df = df.sort_values(column, ascending=False).head(n)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    colors = gradient_bars(ax, top_df[column].values)
    ax.bar(top_df["Player"], top_df[column], color=colors, edgecolor=VOID_2, linewidth=0.6)
    ax.set_title(title or f"Top {n} — {column}", fontsize=13)
    ax.set_ylabel(column)
    plt.setp(ax.get_xticklabels(), rotation=42, ha="right")
    style_axes(fig, ax)
    fig.tight_layout()
    return fig


def chart_histogram(df, column, bins=12, log_scale=False):
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    counts, edges, patches = ax.hist(df[column].dropna(), bins=bins, edgecolor=VOID_2, linewidth=0.6)
    for i, p in enumerate(patches):
        p.set_facecolor(ORANGE_CMAP(0.25 + 0.7 * (i / max(len(patches) - 1, 1))))
    if log_scale:
        ax.set_yscale("log")
    ax.set_title(f"Distribution — {column}" + (" (log scale)" if log_scale else ""), fontsize=13)
    ax.set_xlabel(column)
    ax.set_ylabel("Players")
    style_axes(fig, ax)
    fig.tight_layout()
    return fig


def chart_boxplot(df, column):
    fig, ax = plt.subplots(figsize=(4.6, 4.6))
    bp = ax.boxplot(
        df[column].dropna(), patch_artist=True, widths=0.45,
        boxprops=dict(facecolor=AMBER, color=LINE),
        medianprops=dict(color=VOID, linewidth=2),
        whiskerprops=dict(color=CREAM_DIM), capprops=dict(color=CREAM_DIM),
        flierprops=dict(markerfacecolor=BLAZE, markeredgecolor=RUST, markersize=5, alpha=0.7),
    )
    ax.set_title(f"{column} — Spread", fontsize=13)
    ax.set_xticks([])
    style_axes(fig, ax)
    fig.tight_layout()
    return fig


def chart_category_counts(df):
    counts = df["Category"].value_counts()
    fig, ax = plt.subplots(figsize=(9, 4.6))
    colors = [ORANGE_CMAP(0.2 + 0.7 * i / max(len(counts) - 1, 1)) for i in range(len(counts))]
    ax.bar(counts.index, counts.values, color=colors, edgecolor=VOID_2, linewidth=0.6)
    ax.set_title("Players by Category", fontsize=13)
    ax.set_ylabel("Players")
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    style_axes(fig, ax)
    fig.tight_layout()
    return fig


def chart_average_by_category(df, column):
    avg = df.groupby("Category")[column].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 4.6))
    colors = gradient_bars(ax, avg.values)
    ax.bar(avg.index, avg.values, color=colors, edgecolor=VOID_2, linewidth=0.6)
    ax.set_title(f"Average {column} by Category", fontsize=13)
    ax.set_ylabel(f"Avg. {column}")
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    style_axes(fig, ax)
    fig.tight_layout()
    return fig


def chart_scatter(df, x_col, y_col):
    fig, ax = plt.subplots(figsize=(7.5, 5))
    vals = df[y_col].values
    order = np.argsort(vals)
    ranks = np.argsort(order) / max(len(vals) - 1, 1)
    colors = [ORANGE_CMAP(0.25 + 0.65 * r) for r in ranks]
    ax.scatter(df[x_col], df[y_col], c=colors, s=42, edgecolor=VOID_2, linewidth=0.4, alpha=0.9)
    ax.set_title(f"{x_col} vs {y_col}", fontsize=13)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    style_axes(fig, ax)
    fig.tight_layout()
    return fig


def chart_correlation_heatmap(df, columns):
    corr = df[columns].corr()
    fig, ax = plt.subplots(figsize=(8.5, 6.8))
    im = ax.imshow(corr.values, cmap=ORANGE_CMAP, vmin=-1, vmax=1)
    ax.set_xticks(range(len(columns)))
    ax.set_yticks(range(len(columns)))
    ax.set_xticklabels(columns, rotation=45, ha="right", fontsize=8, color=CREAM_DIM)
    ax.set_yticklabels(columns, fontsize=8, color=CREAM_DIM)
    for i in range(len(columns)):
        for j in range(len(columns)):
            val = corr.values[i, j]
            txt_color = VOID if val > 0.35 else CREAM
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=txt_color, fontsize=7.5)
    ax.set_title("Correlation Between Key Stats", fontsize=13, color=GOLD)
    fig.patch.set_facecolor(VOID_2)
    for spine in ax.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.03)
    cbar.ax.yaxis.set_tick_params(color=CREAM_DIM, labelcolor=CREAM_DIM)
    fig.tight_layout()
    return fig


def chart_player_compare(compare_df):
    fig, ax = plt.subplots(figsize=(9.5, 5))
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
    ax.set_title("Player Comparison", fontsize=13)
    legend = ax.legend(facecolor=EMBER, edgecolor=LINE, labelcolor=CREAM, fontsize=9)
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
        f"""<div class="fl-card">
        <h3>Dataset not found</h3>
        <p class="fl-sub">Could not locate <code>{DATA_PATH}</code>.
        Run <code>cleaning/clean_data.py</code> first to generate
        <code>data/players_cleaned.csv</code>.</p></div>""",
        unsafe_allow_html=True,
    )
    st.stop()

numeric_columns = get_numeric_columns(df)
available_key_stats = [c for c in KEY_STATS if c in df.columns]

# ============================================================================
# 5. SIDEBAR — filters ("team sheet")
# ============================================================================
st.sidebar.markdown(
    """<div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:1.3rem;
    letter-spacing:0.04em;color:#FFE7C2;margin-bottom:0.2rem;">⚽ TEAM SHEET</div>
    <div style="font-size:0.75rem;color:#C99A6E;letter-spacing:0.08em;text-transform:uppercase;
    margin-bottom:1rem;">Filters apply to every tab</div>""",
    unsafe_allow_html=True,
)

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
    st.sidebar.markdown("---")
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

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""<div class="fl-card"><div class="fl-eyebrow" style="color:#FFA33E;">IN VIEW</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:1.8rem;font-weight:700;color:#FFC971;">
    {len(filtered_df)}</div><div style="font-size:0.75rem;color:#C99A6E;">
    of {len(df)} players</div></div>""",
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
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
# 6. HERO
# ============================================================================
st.markdown(
    """
    <div class="fl-hero">
        <div class="fl-eyebrow">CANADA · MEXICO · USA 2026 — PLAYER STATISTICS</div>
        <div class="fl-title">FIFA World Cup 2026<br>Player Analysis</div>
        <div class="fl-sub">Scraped from fifa.com, cleaned, and broken down across eight
        performance categories — attacking, distribution, defending, discipline,
        goalkeeping, movement and physical output. Explore rankings, distributions,
        correlations, and individual player profiles below.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
stat_card(c1, "01", f"{len(filtered_df):,}", "Players in view")
stat_card(c2, "02", filtered_df["Category"].nunique() if "Category" in filtered_df.columns else "—", "Categories")
if "Goal Contribution" in filtered_df.columns:
    avg_gc = filtered_df["Goal Contribution"].mean()
    top_row = filtered_df.loc[filtered_df["Goal Contribution"].idxmax()]
    stat_card(c3, "03", f"{avg_gc:.1f}", "Avg. goal contribution")
    stat_card(c4, "04", top_row["Player"], f"Top contributor · {top_row['Goal Contribution']:.0f}")

# ============================================================================
# 7. TABS
# ============================================================================
tab_home, tab_explorer, tab_compare, tab_stats, tab_insights = st.tabs(
    ["🏠 Home", "🔍 Player Explorer", "⚖️ Compare", "📊 Statistics", "💡 Insights"]
)

# ---- HOME -------------------------------------------------------------
with tab_home:
    pitch_divider("Squad Overview")
    left, right = st.columns([1, 1])
    with left:
        st.markdown("**Players by category**")
        if "Category" in filtered_df.columns:
            fig = chart_category_counts(filtered_df)
            st.pyplot(fig)
            plt.close(fig)
    with right:
        if "Goal Contribution" in filtered_df.columns and "Category" in filtered_df.columns:
            st.markdown("**Average goal contribution by category**")
            fig = chart_average_by_category(filtered_df, "Goal Contribution")
            st.pyplot(fig)
            plt.close(fig)

    pitch_divider("Data Preview")
    st.dataframe(filtered_df.head(25), use_container_width=True, height=320)

    with st.expander("Full descriptive statistics"):
        stats = summary_stats(filtered_df)
        st.dataframe(stats["describe"], use_container_width=True)

# ---- PLAYER EXPLORER ----------------------------------------------------
with tab_explorer:
    pitch_divider("Player Profile")
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

        stat_cols = st.columns(4)
        for i, col in enumerate(available_key_stats[:8]):
            val = row.get(col, np.nan)
            display_val = f"{val:.2f}" if isinstance(val, (int, float, np.floating)) else str(val)
            stat_card(stat_cols[i % 4], f"{i+1:02d}", display_val, col)
            if (i % 4) == 3:
                st.write("")

        pitch_divider("Full Stat Line")
        display_cols = [c for c in numeric_columns if c != "Rank"]
        st.dataframe(row[display_cols].to_frame(name="Value"), use_container_width=True)

# ---- COMPARE ------------------------------------------------------------
with tab_compare:
    pitch_divider("Head to Head")
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
        st.dataframe(compare_df, use_container_width=True)
    else:
        st.info("Pick at least one player and one stat to compare.")

# ---- STATISTICS -----------------------------------------------------------
with tab_stats:
    pitch_divider("Rankings")
    default_stat = "Goal Contribution" if "Goal Contribution" in numeric_columns else numeric_columns[0]
    col_a, col_b = st.columns([2, 1])
    with col_a:
        rank_column = st.selectbox("Stat to rank by", options=numeric_columns, index=numeric_columns.index(default_stat))
    with col_b:
        top_n_value = st.slider("Number of players", 5, 25, 10)

    fig = chart_top_n_bar(filtered_df, rank_column, n=top_n_value)
    st.pyplot(fig)
    plt.close(fig)
    st.dataframe(top_n(filtered_df, rank_column, n=top_n_value), use_container_width=True)

    pitch_divider("Distribution")
    default_dist = "Attempts At Goal" if "Attempts At Goal" in numeric_columns else numeric_columns[0]
    col_c, col_d, col_e = st.columns([2, 1, 1])
    with col_c:
        dist_column = st.selectbox("Stat", options=numeric_columns, index=numeric_columns.index(default_dist), key="dist_col")
    with col_d:
        bins = st.slider("Bins", 5, 40, 12)
    with col_e:
        log_scale = st.checkbox("Log scale", value=False)

    col_left, col_right = st.columns(2)
    with col_left:
        fig = chart_histogram(filtered_df, dist_column, bins=bins, log_scale=log_scale)
        st.pyplot(fig)
        plt.close(fig)
    with col_right:
        fig = chart_boxplot(filtered_df, dist_column)
        st.pyplot(fig)
        plt.close(fig)

    pitch_divider("Correlations")
    corr_columns = st.multiselect(
        "Columns in heatmap", options=numeric_columns,
        default=[c for c in available_key_stats if c in numeric_columns][:8] or numeric_columns[:6],
    )
    if len(corr_columns) >= 2:
        fig = chart_correlation_heatmap(filtered_df, corr_columns)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Select at least two columns to build a heatmap.")

    st.markdown("**Scatter: compare two stats**")
    col_x, col_y = st.columns(2)
    with col_x:
        x_default = "Top Speed (km/h)" if "Top Speed (km/h)" in numeric_columns else numeric_columns[0]
        x_col = st.selectbox("X-axis", options=numeric_columns, index=numeric_columns.index(x_default))
    with col_y:
        y_default = "Goal Contribution" if "Goal Contribution" in numeric_columns else numeric_columns[-1]
        y_col = st.selectbox("Y-axis", options=numeric_columns, index=numeric_columns.index(y_default))
    fig = chart_scatter(filtered_df, x_col, y_col)
    st.pyplot(fig)
    plt.close(fig)

# ---- INSIGHTS ---------------------------------------------------------
with tab_insights:
    pitch_divider("Key Findings")

    insights = []
    if "Category" in filtered_df.columns and "Goal Contribution" in filtered_df.columns:
        best_cat = filtered_df.groupby("Category")["Goal Contribution"].mean().idxmax()
        best_cat_val = filtered_df.groupby("Category")["Goal Contribution"].mean().max()
        insights.append(f"<b>{best_cat}</b> leads all categories with the highest average goal contribution, at <b>{best_cat_val:.2f}</b> per player.")

    if "Top Speed (km/h)" in filtered_df.columns and "Goal Contribution" in filtered_df.columns:
        corr = filtered_df["Top Speed (km/h)"].corr(filtered_df["Goal Contribution"])
        strength = "a strong" if abs(corr) > 0.5 else "a weak" if abs(corr) < 0.2 else "a moderate"
        direction = "positive" if corr > 0 else "negative"
        insights.append(f"Top speed and goal contribution show {strength} {direction} relationship (r = <b>{corr:.2f}</b>).")

    if "Goal Efficiency" in filtered_df.columns and "Attempts At Goal" in filtered_df.columns:
        qualified = filtered_df[filtered_df["Attempts At Goal"] >= filtered_df["Attempts At Goal"].median()]
        if not qualified.empty:
            most_efficient = qualified.loc[qualified["Goal Efficiency"].idxmax()]
            insights.append(f"Among players with at least median shot volume, <b>{most_efficient['Player']}</b> converts most efficiently, at <b>{most_efficient['Goal Efficiency']:.2f}</b>.")

    if "Passing Accuracy (%)" in filtered_df.columns:
        top_passer = filtered_df.loc[filtered_df["Passing Accuracy (%)"].idxmax()]
        insights.append(f"<b>{top_passer['Player']}</b> posts the highest passing accuracy in view, at <b>{top_passer['Passing Accuracy (%)']:.1f}%</b>.")

    if "Total Distance (m)" in filtered_df.columns:
        avg_dist = filtered_df["Total Distance (m)"].mean()
        insights.append(f"Players in view cover an average of <b>{avg_dist:,.0f}m</b> per match on record.")

    if not insights:
        insights.append("Not enough numeric columns available in this dataset view to generate insights.")

    for text in insights:
        st.markdown(f'<div class="fl-insight">{text}</div>', unsafe_allow_html=True)

st.markdown(
    """<div style="text-align:center;color:#C99A6E;font-size:0.75rem;
    letter-spacing:0.08em;text-transform:uppercase;margin-top:2rem;">
    Built with Pandas · NumPy · Matplotlib · Streamlit — Floodlight theme</div>""",
    unsafe_allow_html=True,
)