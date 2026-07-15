import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
COOKIES = os.getenv("YT_COOKIES")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing")

MAX_FILE_SIZE = 49 * 1024 * 1024

DOWNLOAD_DIR = "downloads"
