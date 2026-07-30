import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from analysis.stats import summary_stats, top_n
from analysis.visualizations import (
    KEY_STATS,
    top_n_bar_chart,
    distribution_histogram,
    players_by_category_chart,
    boxplot,
    scatter_chart,
    correlation_heatmap,
    average_by_category_chart,
)

DATA_PATH = ROOT_DIR / "Data" / "players_cleaned.csv"

sns.set_theme(style="whitegrid")

st.set_page_config(
    page_title="FIFA World Cup Player Analysis",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def get_numeric_columns(df: pd.DataFrame) -> list:
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    drop_cols = {"level_1", "Rank"}
    return [c for c in numeric_cols if c not in drop_cols]


try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"Could not find the cleaned dataset at `{DATA_PATH}`.\n\n"
        "Run `cleaning/clean_data.py` first to generate `Data/players_cleaned.csv`."
    )
    st.stop()

numeric_columns = get_numeric_columns(df)

st.sidebar.title("⚽ Filters")

categories = sorted(df["Category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Category", options=categories, default=categories
)

search_term = st.sidebar.text_input("Search player by name")

involvement_col = "Player Involvements" if "Player Involvements" in df.columns else None
if involvement_col:
    max_involvement = int(df[involvement_col].max())
    min_involvement = st.sidebar.slider(
        "Minimum player involvements",
        min_value=0,
        max_value=max_involvement if max_involvement > 0 else 1,
        value=0,
        help="Filters out players with very few recorded involvements/touches.",
    )
else:
    min_involvement = 0

filtered_df = df[df["Category"].isin(selected_categories)] if selected_categories else df.copy()
if involvement_col:
    filtered_df = filtered_df[filtered_df[involvement_col] >= min_involvement]
if search_term:
    filtered_df = filtered_df[
        filtered_df["Player"].str.contains(search_term, case=False, na=False)
    ]

st.sidebar.markdown("---")
st.sidebar.metric("Players in view", len(filtered_df))
st.sidebar.caption("Filters apply to every tab in the dashboard.")

st.title("🏆 FIFA World Cup Player Analysis")
st.caption(
    "Scraped, cleaned, and analyzed player performance data — "
    "explore rankings, distributions, correlations, and individual players below."
)

if filtered_df.empty:
    st.warning("No players match the current filters. Adjust the filters in the sidebar.")
    st.stop()

tab_overview, tab_rankings, tab_distributions, tab_correlations, tab_explorer = st.tabs(
    ["📊 Overview", "🏅 Rankings", "📈 Distributions", "🔗 Correlations", "🔍 Player Explorer"]
)

with tab_overview:
    st.subheader("Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Players", f"{len(filtered_df):,}")
    col2.metric("Categories", filtered_df["Category"].nunique())

    if "Goal Contribution" in filtered_df.columns:
        avg_gc = filtered_df["Goal Contribution"].mean()
        top_scorer_row = filtered_df.loc[filtered_df["Goal Contribution"].idxmax()]
        col3.metric("Avg. Goal Contribution", f"{avg_gc:.2f}")
        col4.metric(
            "Top Goal Contributor",
            top_scorer_row["Player"],
            f"{top_scorer_row['Goal Contribution']:.0f}",
        )

    st.markdown("---")

    left, right = st.columns([1, 1])
    with left:
        st.markdown("**Players by Category**")
        fig = players_by_category_chart(filtered_df)
        st.pyplot(fig)
        plt.close(fig)

    with right:
        st.markdown("**Average Goal Contribution by Category**")
        if "Goal Contribution" in filtered_df.columns:
            fig = average_by_category_chart(filtered_df, column="Goal Contribution")
            st.pyplot(fig)
            plt.close(fig)

    st.markdown("---")
    st.markdown("**Data Preview**")
    st.dataframe(filtered_df.head(25), use_container_width=True)

    with st.expander("Show full descriptive statistics (NumPy / Pandas)"):
        stats = summary_stats(filtered_df)
        st.dataframe(stats["describe"], use_container_width=True)

with tab_rankings:
    st.subheader("Top N Players by Stat")

    default_stat = "Goal Contribution" if "Goal Contribution" in numeric_columns else numeric_columns[0]
    col_a, col_b = st.columns([2, 1])
    with col_a:
        rank_column = st.selectbox(
            "Stat to rank by",
            options=numeric_columns,
            index=numeric_columns.index(default_stat),
        )
    with col_b:
        top_n_value = st.slider("Number of players (N)", min_value=5, max_value=25, value=10)

    fig = top_n_bar_chart(filtered_df, rank_column, n=top_n_value)
    st.pyplot(fig)
    plt.close(fig)

    st.markdown(f"**Top {top_n_value} table for `{rank_column}`**")
    st.dataframe(top_n(filtered_df, rank_column, n=top_n_value), use_container_width=True)

with tab_distributions:
    st.subheader("How is a stat distributed across players?")

    default_dist_col = "Attempts At Goal" if "Attempts At Goal" in numeric_columns else numeric_columns[0]
    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        dist_column = st.selectbox(
            "Stat",
            options=numeric_columns,
            index=numeric_columns.index(default_dist_col),
            key="dist_col",
        )
    with col_b:
        bins = st.slider("Bins", min_value=5, max_value=40, value=10)
    with col_c:
        log_scale = st.checkbox("Log scale (y-axis)", value=False)

    col_left, col_right = st.columns(2)
    with col_left:
        fig = distribution_histogram(filtered_df, dist_column, bins=bins, log_scale=log_scale)
        st.pyplot(fig)
        plt.close(fig)
    with col_right:
        fig = boxplot(filtered_df, dist_column)
        st.pyplot(fig)
        plt.close(fig)

    stats = summary_stats(filtered_df)
    st.markdown("**Summary statistics**")
    summary_table = pd.DataFrame(
        {
            "Mean": [stats["mean"].get(dist_column, np.nan)],
            "Median": [stats["median"].get(dist_column, np.nan)],
            "Std Dev": [stats["std"].get(dist_column, np.nan)],
            "Variance": [stats["var"].get(dist_column, np.nan)],
            "Min": [stats["min"].get(dist_column, np.nan)],
            "Max": [stats["max"].get(dist_column, np.nan)],
        }
    )
    st.dataframe(summary_table, use_container_width=True, hide_index=True)

with tab_correlations:
    st.subheader("Relationships between stats")

    available_key_stats = [c for c in KEY_STATS if c in numeric_columns]
    corr_columns = st.multiselect(
        "Columns to include in the correlation heatmap",
        options=numeric_columns,
        default=available_key_stats or numeric_columns[:6],
    )

    if len(corr_columns) >= 2:
        fig = correlation_heatmap(filtered_df, columns=corr_columns)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Select at least two columns to build a heatmap.")

    st.markdown("---")
    st.markdown("**Scatter: compare two stats**")
    col_x, col_y = st.columns(2)
    with col_x:
        x_default = "Top Speed (km/h)" if "Top Speed (km/h)" in numeric_columns else numeric_columns[0]
        x_col = st.selectbox("X-axis", options=numeric_columns, index=numeric_columns.index(x_default))
    with col_y:
        y_default = "Goal Contribution" if "Goal Contribution" in numeric_columns else numeric_columns[-1]
        y_col = st.selectbox("Y-axis", options=numeric_columns, index=numeric_columns.index(y_default))

    fig = scatter_chart(filtered_df, x_col, y_col)
    st.pyplot(fig)
    plt.close(fig)

with tab_explorer:
    st.subheader("Look up individual players")

    player_options = sorted(filtered_df["Player"].dropna().unique().tolist())
    if not player_options:
        st.info("No players available with the current filters.")
    else:
        selected_player = st.selectbox("Select a player", options=player_options)
        player_row = filtered_df[filtered_df["Player"] == selected_player].iloc[0]

        st.markdown(f"### {selected_player} — {player_row['Category']}")
        display_cols = [c for c in numeric_columns if c != "Rank"]
        player_stats = player_row[display_cols].to_frame(name="Value")
        st.dataframe(player_stats, use_container_width=True)

        st.markdown("---")
        st.markdown("**Compare up to 3 players**")
        compare_players = st.multiselect(
            "Players to compare", options=player_options, default=[selected_player], max_selections=3
        )
        compare_stats = st.multiselect(
            "Stats to compare",
            options=[c for c in KEY_STATS if c in numeric_columns],
            default=[c for c in ["Assists", "Attempts At Goal", "Passes", "Goal Contribution"] if c in numeric_columns],
        )

        if compare_players and compare_stats:
            compare_df = filtered_df[filtered_df["Player"].isin(compare_players)].set_index("Player")[compare_stats]

            fig, ax = plt.subplots(figsize=(10, 5))
            compare_df.T.plot(kind="bar", ax=ax)
            ax.set_title("Player Comparison")
            ax.set_ylabel("Value")
            plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
            ax.legend(title="Player")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

st.markdown("---")
st.caption("Built with Pandas, NumPy, Matplotlib, Seaborn, and Streamlit.") 