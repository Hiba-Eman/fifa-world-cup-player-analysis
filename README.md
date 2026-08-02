# FIFA World Cup 2026 - Player Statistics Analysis

A small data analysis project that scrapes, cleans, analyses, and
visualizes player statistics from the official FIFA World Cup 2026
statistics page, and presents the results in an interactive Streamlit
dashboard.

**Live App:** [View the Streamlit Dashboard](https://fifa2026-player-analysis.streamlit.app/)

**Data source:** [FIFA World Cup 2026 - Player Statistics](https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/statistics/player-statistics)

## Project Structure

```
fifa-world-cup-player-analysis/
│
├── Data/                      # Raw and cleaned CSV files
│   ├── players_raw.csv
│   ├── players_cleaned.csv
│   └── general.csv, attacking.csv, defending.csv, ... (one CSV per FIFA category)
│
├── notebooks/                 # Step-by-step exploratory notebooks
│   ├── 01_data_scraping.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_statistical_analysis.ipynb
│   └── 04_visualizations.ipynb
│
├── scraping/
│   └── scraper.py             # Script version of the scraping notebook
│
├── cleaning/
│   └── clean_data.py          # Script version of the cleaning notebook
│
├── analysis/
│   ├── stats.py          # Descriptive stats + top-N rankings
│   └── visualizations.py      # Reusable chart functions (used by the dashboard)
│
├── dashboard/
│   └── app.py                 # Streamlit dashboard
│
├── requirements.txt
└── README.md
```

## About the Data

Player stats are scraped from FIFA's "Player Statistics" page, which is
split into 8 categories: **General, Attacking, Distribution, Defending,
Discipline, Goalkeeping, Movement, and Physical**. Each category has its
own table with different columns, so all 8 tables are saved separately
in `Data/` and also combined into one long-format file, `players_raw.csv`
(one row per player per category).

After cleaning, `players_cleaned.csv` adds two new features:

- **Goal Contribution** = Assists + Attempts At Goal
- **Goal Efficiency** = Assists / Attempts At Goal (0 if a player has no attempts)

## How to Run

1. Install the requirements:

   ```bash
   pip install -r requirements.txt
   ```

2. **(Optional) Re-scrape the data.** The CSV files in `Data/` are
   already provided, so this step can be skipped unless you want fresh
   data:

   ```bash
   cd scraping
   python scraper.py
   ```

3. **(Optional) Re-run the cleaning step.** `players_cleaned.csv` is
   already provided, but you can regenerate it from
   `players_raw.csv`:

   ```bash
   cd cleaning
   python clean_data.py
   ```

4. **Explore the notebooks** in order (01 → 04) using Jupyter:

   ```bash
   jupyter notebook notebooks/
   ```

5. **Run the dashboard:**

   ```bash
   python -m streamlit run dashboard/app.py
   ```

## Note on `analysis/statistics.py`

This file is named to match the project structure, but it happens to
share its name with Python's built-in `statistics` module. This is
fine for the way it's used in this project (imported normally, or run
directly with `python statistics.py`), but avoid running
`analysis/visualizations.py` on its own from inside the `analysis/`
folder — it imports `seaborn`, which internally needs Python's real
`statistics` module, and running it that way can make Python pick up
our file instead. It works correctly when imported from the dashboard
or a notebook, which is how it's meant to be used.

## Notes

- The scraper uses Selenium + a real Chrome browser, so it needs Google
  Chrome installed locally to re-run.
- Charts generated in `04_visualizations.ipynb` are also saved as PNG
  files in a `visuals/` folder (created automatically) for easy reuse.
- This is a beginner-level university project — the focus is on clean,
  readable code and a clear pipeline (scrape → clean → analyse →
  visualize → dashboard), not on advanced engineering.
