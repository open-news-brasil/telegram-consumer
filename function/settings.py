from os import getenv


TELEGRAM_MAX_CONTENT_SIZE = 790
TELEGRAM_MAX_ALBUM_QUANTITY = 10

TELEGRAM_API_ID = getenv("TELEGRAM_API_ID", "")
TELEGRAM_API_HASH = getenv("TELEGRAM_API_HASH", "")
TELEGRAM_BOT_TOKENS = [
    token for i in range(5) if (token := getenv(f"TELEGRAM_BOT_REPLICA_{i}_TOKEN"))
]

WHATSAPP_LINK_TEMPLATE = "https://api.whatsapp.com/send?text={text}"
WHATSAPP_LINK_FOR_CHANNEL = "t.me/s/noticias_phb"
