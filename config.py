import os
from dotenv import load_dotenv

load_dotenv()

# Telegram settings
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT")

# Earthquake monitoring settings
UPDATE_FREQUENCY_MINUTES = int(os.getenv("UPDATE_FREQUENCY_MINUTES"))  # Частота проверки (минуты)
MAGNITUDE_THRESHOLD = float(os.getenv("MAGNITUDE_THRESHOLD"))  # Порог магнитуды для публикации
USGS_API_URL = os.getenv("USGS_API_URL", "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson")