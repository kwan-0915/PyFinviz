import os
import warnings
import requests
import pandas as pd
from tqdm.auto import tqdm
from bs4 import BeautifulSoup
from pyfinviz import Screener

warnings.filterwarnings("ignore")

dest_dir = os.path.join(os.getcwd(), "data")
if not os.path.exists(dest_dir): os.makedirs(dest_dir)

def main():
    custom_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    url = "https://finviz.com/screener"

    response = requests.get(url=url, headers=custom_headers)
    if response.status_code != 200: raise ValueError("Invalid status code")

    soup = BeautifulSoup(response.text, "html.parser")
    num_page = soup.find_all("a", {"class": "screener-pages"})[-2].text

    if not num_page.isnumeric(): raise ValueError(f"Invalid page number, {num_page}")

    pages, all_ticker = [i for i in range(1, int(num_page) + 1)], []
    for i in tqdm(pages, total=len(pages), desc="Downloading finviz data"):
        try:
            screener = Screener(pages=[i])

            all_ticker.append(screener.data_frames[i])

        except Exception as e: print(f"Error: {e}, page {i}")

    all_ticker = pd.concat(all_ticker)
    if not all_ticker.empty:
        if "No" in all_ticker.columns.tolist(): all_ticker = all_ticker.drop(columns=["No"], axis=1)

        all_ticker.to_csv(os.path.join(dest_dir, f"{pd.Timestamp.now().__str__().split(' ')[0]}.csv"), index=False)

if __name__ == "__main__":
    main()