import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

URL = "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/statistics/player-statistics"

CATEGORIES = [
    "General",
    "Attacking",
    "Distribution",
    "Defending",
    "Discipline",
    "Goalkeeping",
    "Movement",
    "Physical",
]

def start_driver():
    """Launch the Chrome browser and open the FIFA statistics page."""
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(URL)
    time.sleep(5)
    return driver

def click_category(driver, category):
    """Click on a category tab on the FIFA statistics page."""
    if category == "General":
        return

    button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, f"//button[normalize-space()='{category}']"))
    )
    driver.execute_script("arguments[0].click();", button)
    time.sleep(5)
    print(category, "opened")

def extract_table(driver):
    """Read the currently visible table on the page into a DataFrame."""
    # Wait up to 15 seconds for the table element to load into the DOM
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find("table")

    if not table:
        print("Warning: Table element not found!")
        return pd.DataFrame()

    rows = table.find_all("tr")

    headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]

    data = []
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) == 0:
            continue

        row_data = []
        for index, col in enumerate(cols):
            if index == 1:
                player_name = col.find("div", class_="main-text")
                row_data.append(player_name.get_text(strip=True) if player_name else col.get_text(strip=True))
            else:
                row_data.append(col.get_text(strip=True))

        data.append(row_data)

    return pd.DataFrame(data, columns=headers)

def scrape_all_categories(driver):
    """Click through every category and collect its table."""
    all_tables = {}

    for category in CATEGORIES:
        print("\nExtracting:", category)
        click_category(driver, category)
        df = extract_table(driver)
        all_tables[category] = df
        print(category, df.shape)

    return all_tables

def save_category_files(all_tables, output_dir="Data"):
    """Save each category table as its own CSV file."""
    for category, df in all_tables.items():
        filename = f"{output_dir}/{category.lower()}.csv"
        df.to_csv(filename, index=False)

    print("Category files saved")

def build_raw_dataset(all_tables):
    """Combine all category tables into a single raw dataset."""
    combined_df = pd.concat(all_tables.values(), keys=all_tables.keys())
    combined_df = combined_df.reset_index()
    combined_df.rename(columns={"level_0": "Category"}, inplace=True)
    return combined_df

def main():
    driver = start_driver()

    try:
        all_tables = scrape_all_categories(driver)
        save_category_files(all_tables)

        combined_df = build_raw_dataset(all_tables)
        combined_df.to_csv("Data/players_raw.csv", index=False)
        print("players_raw.csv created successfully!")
        print(combined_df.shape)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
