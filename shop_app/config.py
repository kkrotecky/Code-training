import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = Path(__file__).parent
ITEMS_CSV = BASE_DIR / "items.csv"
PROFILE_JSON = BASE_DIR / "user_profile.json"

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SMTP_EMAIL")
SENDER_PASSWORD = os.getenv("SMTP_PASSWORD")
SHOP_EMAIL = os.getenv("SHOP_EMAIL")
def validate_email_config():
    missing = [k for k in ("SENDER_EMAIL", "SENDER_PASSWORD", "SHOP_EMAIL") if not globals()[k]]
    if missing:
        raise RuntimeError(f"Missing email env vars: {', '.join(missing)}")