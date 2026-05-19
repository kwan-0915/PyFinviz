import os
import warnings
import requests
import pandas as pd
from tqdm.auto import tqdm
from bs4 import BeautifulSoup
from pyfinviz import Screener

warnings.filterwarnings("ignore")

root_dir = os.path.join(os.getcwd(), "data")
if not os.path.exists(root_dir): os.makedirs(root_dir)

custom_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def download_finviz():
    dest_dir = os.path.join(root_dir, "finviz")
    if not os.path.exists(dest_dir): os.makedirs(dest_dir)

    url = "https://finviz.com/screener"

    response = requests.get(url=url, headers=custom_headers)
    if response.status_code != 200: raise ValueError("Invalid status code")

    soup = BeautifulSoup(response.text, "html.parser")
    num_page = soup.find_all("a", {"class": "screener-pages"})[-2].text

    if not num_page.isnumeric(): raise ValueError(f"Invalid page number, {num_page}")

    pages, all_ticker = [i for i in range(1, int(num_page) + 1)], []
    for i in tqdm(pages, total=len(pages), desc="Downloading Finviz"):
        try:
            screener = Screener(pages=[i])

            all_ticker.append(screener.data_frames[i])

        except Exception as e: print(f"Error: {e}, page {i}")

    all_ticker = pd.concat(all_ticker)
    if not all_ticker.empty:
        if "No" in all_ticker.columns.tolist(): all_ticker = all_ticker.drop(columns=["No"], axis=1)

        all_ticker.to_csv(os.path.join(dest_dir, f"Finviz_{pd.Timestamp.now().__str__().split(' ')[0]}.csv"), index=False)

def download_ishares():
    russel_url = "https://www.blackrock.com/varnish-api/blk-one01-product-data/product-data/api/v1/get-fund-document?appType=PRODUCT_PAGE&appSubType=ISHARES&targetSite=us-ishares&locale=en_US"

    url_mapper = {
        "CNDX": "https://www.ishares.com/ch/professionals/en/products/253741/ishares-nasdaq-100-ucits-etf/1495092304805.ajax?fileType=csv&fileName=CSNDX_holdings&dataType=fund",
        "IVV": "https://www.ishares.com/ch/professionals/en/products/239726/ishares-core-sp-500-etf/1495092304805.ajax?fileType=csv&fileName=IVV_holdings&dataType=fund",
        "IWB": f"{russel_url}&portfolioId=239707&userType=individual&asOfDate=20260518&component=holdings",
        "IWM": f"{russel_url}&portfolioId=239710&userType=individual&asOfDate=20260518&component=holdings",
        "IWV": f"{russel_url}&portfolioId=239714&userType=individual&asOfDate=20260518&component=holdings"
    }

    for product, url in tqdm(url_mapper.items(), total=len(url_mapper.keys()), desc="Downloading iShares"):
        try:
            response = requests.get(url=url, headers=custom_headers)
            if response.status_code != 200: raise ValueError("Invalid status code")

            dest_dir = os.path.join(root_dir, "ishares", product)
            if not os.path.exists(dest_dir): os.makedirs(dest_dir)

            with open(os.path.join(dest_dir, f"{product}_{pd.Timestamp.now().__str__().split(' ')[0]}.csv"), "wb") as f:
                f.write(response.content)

        except Exception as e: print(f"[{product}] Error: {e}")

if __name__ == "__main__":
    download_finviz()

    download_ishares()