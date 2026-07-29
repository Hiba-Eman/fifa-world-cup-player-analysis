import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

KEY_STATS = [
    "Assists",
    "Attempts At Goal",
    "Passes",
    "Passing Accuracy (%)",
    "Top Speed (km/h)",
    "Total Distance (m)",
    "Goal Contribution",
    "Goal Efficiency",
]

def top_n_bar_chart(df, column, n=10, color="skyblue"):
    """Bar chart of the top n players for a given numeric column."""
    top_df = df.sort_values(column, ascending=False).head(n)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(top_df["Player"], top_df[column], color=color)
    ax.set_title(f"Top {n} Players by {column}")
    ax.set_xlabel("Player")
    ax.set_ylabel(column)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    return fig

def distribution_histogram(df, column, bins=10, log_scale=False, color="teal"):
    """Histogram showing how a numeric column is distributed."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df[column], bins=bins, color=color)

    if log_scale:
        ax.set_yscale("log")

    title = f"Distribution of {column}"
    if log_scale:
        title += " (Log Scale)"

    ax.set_title(title)
    ax.set_xlabel(column)
    ax.set_ylabel("Number of Players")
    fig.tight_layout()
    return fig

def players_by_category_chart(df):
    """Count plot showing how many players are in each stats category."""
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.countplot(data=df, x="Category", ax=ax)
    ax.set_title("Number of Players by Category")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    return fig

def boxplot(df, column):
    """Boxplot for a single numeric column."""
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(y=df[column], ax=ax)
    ax.set_title(f"{column} Boxplot")
    fig.tight_layout()
    return fig

def scatter_chart(df, x_column, y_column, color="purple"):
    """Scatter plot comparing two numeric columns."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df[x_column], df[y_column], color=color)
    ax.set_title(f"{x_column} vs {y_column}")
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    fig.tight_layout()
    return fig

def correlation_heatmap(df, columns=None):
    """Heatmap showing correlation between key numeric stats."""
    columns = columns or KEY_STATS
    corr = df[columns].corr()

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    ax.set_title("Correlation Between Key Player Stats")
    fig.tight_layout()
    return fig

def average_by_category_chart(df, column="Goal Contribution", color="coral"):
    """Bar chart of the average value of a column, grouped by category."""
    avg_by_category = df.groupby("Category")[column].mean().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    avg_by_category.plot(kind="bar", color=color, ax=ax)
    ax.set_title(f"Average {column} by Category")
    ax.set_xlabel("Category")
    ax.set_ylabel(f"Average {column}")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    return fig

def main():
    df = pd.read_csv("Data/players_cleaned.csv")

    top_n_bar_chart(df, "Goal Contribution")
    distribution_histogram(df, "Attempts At Goal")
    players_by_category_chart(df)
    correlation_heatmap(df)
    boxplot(df, "Goal Contribution")
    scatter_chart(df, "Top Speed (km/h)", "Goal Contribution")
    average_by_category_chart(df)

    plt.show()

if __name__ == "__main__":
    main()