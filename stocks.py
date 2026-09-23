import requests
import pandas as pd
from io import StringIO

URL = "https://www.oyakyatirim.com.tr/piyasa-verileri/XUTUM"


def get_bist_tum_stocks():

    response = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    response.raise_for_status()

    tables = pd.read_html(StringIO(response.text))

    for table in tables:

        if "Sembol" in table.columns:

            symbols = (
                table["Sembol"]
                .astype(str)
                .str.strip()
                .str.upper()
                .tolist()
            )

            stocks = [
                f"{symbol}.IS"
                for symbol in symbols
                if symbol.isalnum() and 2 <= len(symbol) <= 6
            ]

            if stocks:
                return sorted(set(stocks))

    raise RuntimeError("BIST TUM hisse listesi bulunamadı.")


STOCKS = get_bist_tum_stocks()

print(f"BIST TUM hisseleri yüklendi: {len(STOCKS)} adet")
