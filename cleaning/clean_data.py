import pandas as pd
import numpy as np

def load_raw_data(path="Data/players_raw.csv"):
    return pd.read_csv(path)

def strip_text_columns(df):
    """Remove extra spaces from text columns."""
    df["Player"] = df["Player"].str.strip()
    df["Category"] = df["Category"].str.strip()
    return df

def clean_xg_efficiency(df):
    """Remove the trailing 'x' from the xG Efficiency column and convert it to a number."""
    df["xG Efficiency"] = df["xG Efficiency"].str.replace("x", "", regex=False)
    df["xG Efficiency"] = pd.to_numeric(df["xG Efficiency"], errors="coerce").fillna(0)
    return df

def fill_missing_values(df):
    """Fill missing numeric values with 0."""
    numeric_cols = df.select_dtypes(include=["number"]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    return df

def add_goal_contribution(df):
    """Goal Contribution = Assists + Attempts At Goal."""
    df["Goal Contribution"] = df["Assists"] + df["Attempts At Goal"]
    return df

def add_goal_efficiency(df):
    """Goal Efficiency = Assists / Attempts At Goal (0 if no attempts)."""
    df["Goal Efficiency"] = np.where(
        df["Attempts At Goal"] > 0,
        df["Assists"] / df["Attempts At Goal"],
        0,
    )
    return df

def clean_data(path="Data/players_raw.csv"):
    """Run the full cleaning pipeline and return the cleaned DataFrame."""
    df = load_raw_data(path)
    df = strip_text_columns(df)
    df = clean_xg_efficiency(df)
    df = fill_missing_values(df)
    df = add_goal_contribution(df)
    df = add_goal_efficiency(df)
    return df

def main():
    df = clean_data()
    df.to_csv("Data/players_cleaned.csv", index=False)
    print("players_cleaned.csv created successfully!")
    print(df.shape)

if __name__ == "__main__":
    main()
