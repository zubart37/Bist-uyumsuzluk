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
# BIST 50 HİSSELERİ
# ==========================================


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
        window = series.iloc[i-left:i+right+1]

        if (
            series.iloc[i] == window.min()
            and (window == series.iloc[i]).sum() == 1
        ):
            pivots.append(i)

    return pivots


def find_pivot_highs(series, left=3, right=3):
    pivots = []

    for i in range(left, len(series) - right):
        window = series.iloc[i-left:i+right+1]

        if (
            series.iloc[i] == window.max()
            and (window == series.iloc[i]).sum() == 1
        ):
            pivots.append(i)

    return pivots


# ==========================================
# UYUMSUZLUK KONTROLÜ
# ==========================================

def check_divergence(data):

    if len(data) < 100:
        return []

    data = data.copy()

    data["RSI"] = calculate_rsi(data["Close"])

    # Son 6 ay civarında çalış
    data = data.tail(180).copy()

    lows = find_pivot_lows(data["Low"])
    highs = find_pivot_highs(data["High"])

    signals = []

    # --------------------------------------
    # POZİTİF UYUMSUZLUK
    # Fiyat: Daha düşük dip
    # RSI: Daha yüksek dip
    # --------------------------------------

    if len(lows) >= 2:

        first = lows[-2]
        second = lows[-1]

        price1 = data["Low"].iloc[first]
        price2 = data["Low"].iloc[second]

        rsi1 = data["RSI"].iloc[first]
        rsi2 = data["RSI"].iloc[second]

        if (
            price2 < price1
            and rsi2 > rsi1
            and not pd.isna(rsi1)
            and not pd.isna(rsi2)
        ):
            signals.append({
                "type": "POZİTİF UYUMSUZLUK",
                "date": data.index[second].strftime("%Y-%m-%d"),
                "price1": round(price1, 2),
                "price2": round(price2, 2),
                "rsi1": round(rsi1, 2),
                "rsi2": round(rsi2, 2)
            })

    # --------------------------------------
    # NEGATİF UYUMSUZLUK
    # Fiyat: Daha yüksek tepe
    # RSI: Daha düşük tepe
    # --------------------------------------

    if len(highs) >= 2:

        first = highs[-2]
        second = highs[-1]

        price1 = data["High"].iloc[first]
        price2 = data["High"].iloc[second]

        rsi1 = data["RSI"].iloc[first]
        rsi2 = data["RSI"].iloc[second]

        if (
            price2 > price1
            and rsi2 < rsi1
            and not pd.isna(rsi1)
            and not pd.isna(rsi2)
        ):
            signals.append({
                "type": "NEGATİF UYUMSUZLUK",
                "date": data.index[second].strftime("%Y-%m-%d"),
                "price1": round(price1, 2),
                "price2": round(price2, 2),
                "rsi1": round(rsi1, 2),
                "rsi2": round(rsi2, 2)
            })

    return signals


# ==========================================
# 50 HİSSEYİ TARA
# ==========================================

def scan_stocks():

    print("=" * 50)
    print("BIST 50 UYUMSUZLUK TARAMASI")
    print("Periyot: 1D")
    print("Gösterge: RSI(14)")
    print("=" * 50)

    total_signals = 0

    for symbol in STOCKS:

        try:

            print(f"\nTaranıyor: {symbol}")

            data = yf.download(
                symbol,
                period="1y",
                interval="1d",
                auto_adjust=False,
                progress=False
            )

            if data.empty:
                print("Veri bulunamadı.")
                continue

            # Bazı yfinance sürümlerinde kolonlar MultiIndex olabilir
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            required = ["High", "Low", "Close"]

            if not all(column in data.columns for column in required):
                print("Gerekli fiyat verileri bulunamadı.")
                continue

            signals = check_divergence(data)

            if signals:

                for signal in signals:

                    print("\n🚨 SİNYAL BULUNDU")
                    print(f"Hisse: {symbol}")
                    print(f"Tür: {signal['type']}")
                    print(f"Tarih: {signal['date']}")
                    print(
                        f"Fiyat: {signal['price1']} → "
                        f"{signal['price2']}"
                    )
                    print(
                        f"RSI: {signal['rsi1']} → "
                        f"{signal['rsi2']}"
                    )
message = (
    "🚨 BIST UYUMSUZLUK\n\n"
    f"{'🟢' if signal['type'] == 'POZİTİF UYUMSUZLUK' else '🔴'} "
    f"{signal['type']}\n"
    f"Hisse: {symbol.replace('.IS', '')}\n"
    "Periyot: 1D\n"
    "Gösterge: RSI(14)\n\n"
    f"Fiyat: {signal['price1']} → {signal['price2']}\n"
    f"RSI: {signal['rsi1']} → {signal['rsi2']}\n\n"
    f"Tarih: {signal['date']}"
)

send_telegram(message)
                    total_signals += 1

            else:
                print("Sinyal yok.")

        except Exception as error:

            print(
                f"Hata oluştu: {symbol} -> {error}"
            )

    print("\n" + "=" * 50)
    print(f"Tarama tamamlandı. Toplam sinyal: {total_signals}")
    print("=" * 50)


# ==========================================
# PROGRAMI BAŞLAT
# ==========================================

if __name__ == "__main__":
    scan_stocks()