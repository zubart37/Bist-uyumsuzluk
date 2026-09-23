import os
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN bulunamadı")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# Botu daha önce kullanan son sohbeti bul
updates = requests.get(
    f"{BASE_URL}/getUpdates",
    timeout=20
).json()

if not updates.get("ok"):
    raise RuntimeError("Telegram bağlantısı başarısız")

results = updates.get("result", [])

if not results:
    raise RuntimeError(
        "Telegram'dan mesaj bulunamadı. Botu açıp /start gönder."
    )

chat_id = results[-1]["message"]["chat"]["id"]

message = (
    "✅ BIST Uyumsuzluk Tarayıcı bağlantısı başarılı!\n\n"
    "Telegram bildirim sistemi çalışıyor.\n"
    "Bir sonraki aşamada BIST taraması eklenecek."
)

response = requests.post(
    f"{BASE_URL}/sendMessage",
    data={
        "chat_id": chat_id,
        "text": message
    },
    timeout=20
)

response.raise_for_status()

print("Telegram test mesajı gönderildi.")