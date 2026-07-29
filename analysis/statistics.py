import pandas as pd

def load_cleaned_data(path="Data/players_cleaned.csv"):
    return pd.read_csv(path)

def summary_stats(df):
    """Return the standard set of descriptive statistics for numeric columns."""
    return {
        "describe": df.describe(),
        "mean": df.mean(numeric_only=True),
        "median": df.median(numeric_only=True),
        "mode": df.mode(numeric_only=True).iloc[0],
        "std": df.std(numeric_only=True),
        "var": df.var(numeric_only=True),
        "min": df.min(numeric_only=True),
        "max": df.max(numeric_only=True),
        "percentiles": df.quantile([0.25, 0.50, 0.75], numeric_only=True),
    }

def top_n(df, column, n=10):
    """Return the top n players sorted by a given column."""
    return df[["Player", column]].sort_values(by=column, ascending=False).head(n)

def top_goal_contributions(df, n=10):
    return top_n(df, "Goal Contribution", n)

def top_assists(df, n=10):
    return top_n(df, "Assists", n)

def top_attempts_at_goal(df, n=10):
    return top_n(df, "Attempts At Goal", n)

def top_passes(df, n=10):
    return top_n(df, "Passes", n)

def top_speed(df, n=10):
    return top_n(df, "Top Speed (km/h)", n)

def main():
    df = load_cleaned_data()

    print("Dataset overview:")
    print(df.describe())

    print("\nTop 10 Goal Contributions:")
    print(top_goal_contributions(df))

    print("\nTop 10 Assists:")
    print(top_assists(df))

    print("\nTop 10 Attempts At Goal:")
    print(top_attempts_at_goal(df))

    print("\nTop 10 Passes:")
    print(top_passes(df))

    print("\nTop 10 Top Speed:")
    print(top_speed(df))

if __name__ == "__main__":
    main()
