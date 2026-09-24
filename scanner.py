import yfinance as yf
import pandas as pd
import numpy as np
from stocks import STOCKS
import os
import requests


# ==========================================
# TELEGRAM
# ==========================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def send_telegram(message):

    if not TELEGRAM_TOKEN:
        print("Telegram token bulunamadı.")
        return

    base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

    try:

        updates = requests.get(
            f"{base_url}/getUpdates",
            timeout=20
        ).json()

        results = updates.get("result", [])

        if not results:
            print("Telegram sohbeti bulunamadı.")
            return

        chat_id = results[-1]["message"]["chat"]["id"]

        requests.post(
            f"{base_url}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": message
            },
            timeout=20
        )

        print("Telegram bildirimi gönderildi.")

    except Exception as error:

        print(f"Telegram hatası: {error}")


# ==========================================
# RSI HESAPLAMA
# ==========================================

def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    rsi = 100 - (100 / (1 + rs))

    return rsi


# ==========================================
# PİVOT BULMA
# ==========================================

def find_pivot_lows(series, left=3, right=3):

    pivots = []

    for i in range(left, len(series) - right):

        window = series.iloc[
            i-left:i+right+1
        ]

        if (
            series.iloc[i] == window.min()
            and
            (window == series.iloc[i]).sum() == 1
        ):

            pivots.append(i)

    return pivots


def find_pivot_highs(series, left=3, right=3):

    pivots = []

    for i in range(left, len(series) - right):

        window = series.iloc[
            i-left:i+right+1
        ]

        if (
            series.iloc[i] == window.max()
            and
            (window == series.iloc[i]).sum() == 1
        ):

            pivots.append(i)

    return pivots


# ==========================================
# UYUMSUZLUK KONTROLÜ
# ==========================================

def check_divergence(data):

    MIN_PIVOT_DISTANCE = 10

    if len(data) < 100:
        return []

    data = data.copy()

    data["RSI"] = calculate_rsi(
        data["Close"]
    )

    # Son 180 günlük veri
    data = data.tail(180).copy()

    signals = []

    # ==========================================
    # SON TAMAMLANMIŞ GÜNLÜK MUM
    # ==========================================

    current_index = len(data) - 1

    current_date = data.index[current_index]

    current_low = data["Low"].iloc[current_index]

    current_high = data["High"].iloc[current_index]

    current_rsi = data["RSI"].iloc[current_index]

    # Son mum dışındaki geçmiş
    previous_data = data.iloc[:-1].copy()

    # ==========================================
    # ÖNCEKİ DİPLER
    # ==========================================

    lows = find_pivot_lows(
        previous_data["Low"],
        left=3,
        right=3
    )

    # ==========================================
    # POZİTİF UYUMSUZLUK
    #
    # Son mum:
    # Daha düşük dip
    # RSI daha yüksek dip
    #
    # Minimum 10 mum mesafe
    # ==========================================

    positive_candidates = []

    for pivot in lows:

        # previous_data içindeki pivot ile
        # son mum arasındaki mesafe
        distance = (
            current_index - pivot
        )

        if distance < MIN_PIVOT_DISTANCE:
            continue

        price1 = previous_data["Low"].iloc[pivot]

        rsi1 = previous_data["RSI"].iloc[pivot]

        if (
            current_low < price1
            and current_rsi > rsi1
            and not pd.isna(rsi1)
            and not pd.isna(current_rsi)
        ):

            positive_candidates.append({
                "pivot": pivot,
                "price1": price1,
                "price2": current_low,
                "rsi1": rsi1,
                "rsi2": current_rsi
            })

    if positive_candidates:

        candidate = positive_candidates[-1]

        signals.append({
            "type": "POZİTİF UYUMSUZLUK",
            "date": current_date.strftime(
                "%Y-%m-%d"
            ),
            "price1": round(
                candidate["price1"], 2
            ),
            "price2": round(
                candidate["price2"], 2
            ),
            "rsi1": round(
                candidate["rsi1"], 2
            ),
            "rsi2": round(
                candidate["rsi2"], 2
            )
        })

    # ==========================================
    # ÖNCEKİ TEPELER
    # ==========================================

    highs = find_pivot_highs(
        previous_data["High"],
        left=3,
        right=3
    )

    # ==========================================
    # NEGATİF UYUMSUZLUK
    #
    # Son mum:
    # Daha yüksek tepe
    # RSI daha düşük tepe
    #
    # Minimum 10 mum mesafe
    # ==========================================

    negative_candidates = []

    for pivot in highs:

        distance = (
            current_index - pivot
        )

        if distance < MIN_PIVOT_DISTANCE:
            continue

        price1 = previous_data["High"].iloc[pivot]

        rsi1 = previous_data["RSI"].iloc[pivot]

        if (
            current_high > price1
            and current_rsi < rsi1
            and not pd.isna(rsi1)
            and not pd.isna(current_rsi)
        ):

            negative_candidates.append({
                "pivot": pivot,
                "price1": price1,
                "price2": current_high,
                "rsi1": rsi1,
                "rsi2": current_rsi
            })

    if negative_candidates:

        candidate = negative_candidates[-1]

        signals.append({
            "type": "NEGATİF UYUMSUZLUK",
            "date": current_date.strftime(
                "%Y-%m-%d"
            ),
            "price1": round(
                candidate["price1"], 2
            ),
            "price2": round(
                candidate["price2"], 2
            ),
            "rsi1": round(
                candidate["rsi1"], 2
            ),
            "rsi2": round(
                candidate["rsi2"], 2
            )
        })

    return signals


# ==========================================
# BIST TÜM HİSSELERİ TARA
# ==========================================

def scan_stocks():

    print("=" * 50)

    print(
        "BIST TÜM GÜNLÜK UYUMSUZLUK TARAMASI"
    )

    print("Periyot: 1D")
    print("Gösterge: RSI(14)")

    print(
        f"Toplam hisse: {len(STOCKS)}"
    )

    print("=" * 50)

   
