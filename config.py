import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file if present

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID"))

# Optional with defaults
SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "https://t.me/your_support_chat")
DEVELOPER = os.environ.get("DEVELOPER", "https://t.me/your_developer_username")
START_PHOTO = os.environ.get("START_PHOTO", "https://telegra.ph/file/your_photo_url_here.jpg")
