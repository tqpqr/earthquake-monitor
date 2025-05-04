import requests
import logging
import schedule
import time
import subprocess
import os
import sys

from config import USGS_API_URL, MAGNITUDE_THRESHOLD, UPDATE_FREQUENCY_MINUTES

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COORDINATES_FILE = os.path.join(BASE_DIR, "coordinates.txt")
LAST_EVENT_FILE = os.path.join(BASE_DIR, "last_event.txt")
LAST_MAGNITUDE_FILE = os.path.join(BASE_DIR, "last_magnitude.txt")
MONOLITH_SCRIPT = os.path.join(BASE_DIR, "monolith.py")

def check_earthquakes():
    logger.info("Fetching latest earthquake data")
    try:
        response = requests.get(USGS_API_URL)
        response.raise_for_status()
        data = response.json()
        
        # Проверяем, есть ли землетрясения
        if not data["features"]:
            logger.info("No earthquakes found")
            return
        
        # Находим последнее землетрясение
        latest_quake = data["features"][0]
        magnitude = latest_quake["properties"]["mag"]
        place = latest_quake["properties"]["place"]
        event_url = latest_quake["properties"]["url"]
        
        logger.debug(f"Found earthquake: {place}, magnitude: {magnitude}")
        
        # Проверяем порог магнитуды
        if magnitude < MAGNITUDE_THRESHOLD:
            logger.info(f"Earthquake magnitude {magnitude} below threshold {MAGNITUDE_THRESHOLD}, skipping")
            return
        
        # Сохраняем координаты
        coordinates = latest_quake["geometry"]["coordinates"]
        longitude, latitude = coordinates[0], coordinates[1]
        # Валидация координат
        if not (-180 <= longitude <= 180):
            logger.error(f"Invalid longitude: {longitude}")
            return
        if not (-90 <= latitude <= 90):
            logger.error(f"Invalid latitude: {latitude}")
            return
        logger.info(f"Saving coordinates: latitude={latitude}, longitude={longitude}")
        with open(COORDINATES_FILE, "w") as f:
            f.write(f"{latitude},{longitude}")
        logger.debug(f"Successfully saved content to {COORDINATES_FILE}")
        
        # Проверяем, новое ли это событие
        logger.info("Checking if this is a new event")
        last_event = None
        if os.path.exists(LAST_EVENT_FILE):
            with open(LAST_EVENT_FILE, "r") as f:
                last_event = f.read().strip()
        
        if last_event != event_url:
            logger.info("Processing new event")
            with open(LAST_EVENT_FILE, "w") as f:
                f.write(event_url)
            with open(LAST_MAGNITUDE_FILE, "w") as f:
                f.write(str(magnitude))
            
            logger.info(f"Processing new earthquake: {place} (M{magnitude})")
            logger.info(f"Using Python executable: {sys.executable}")
            logger.info(f"Running: {sys.executable} {MONOLITH_SCRIPT}")
            
            try:
                result = subprocess.run(
                    [sys.executable, MONOLITH_SCRIPT],
                    capture_output=True,
                    text=True,
                    check=True
                )
                logger.info("Subprocess completed successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"Subprocess error code: {e.returncode}")
                logger.error(f"Subprocess output: {e.stdout}")
                logger.error(f"Subprocess error: {e.stderr}")
                # Сохраняем последнее событие, чтобы избежать повторов
                with open(LAST_EVENT_FILE, "w") as f:
                    f.write(event_url)
        else:
            logger.info("No new earthquake event")
            
    except Exception as e:
        logger.error(f"Error fetching earthquake data: {str(e)}")

if __name__ == "__main__":
    logger.info(f"Script directory: {BASE_DIR}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"BASE_DIR: {BASE_DIR}")
    logger.info(f"COORDINATES_FILE: {COORDINATES_FILE}")
    logger.info(f"LAST_EVENT_FILE: {LAST_EVENT_FILE}")
    logger.info(f"LAST_MAGNITUDE_FILE: {LAST_MAGNITUDE_FILE}")
    logger.info(f"MONOLITH_SCRIPT: {MONOLITH_SCRIPT}")
    logger.info(f"MONOLITH_SCRIPT exists: {os.path.exists(MONOLITH_SCRIPT)}")
    logger.info("Starting earthquake monitoring script")
    
    # Настройка расписания
    schedule.every(UPDATE_FREQUENCY_MINUTES).minutes.do(check_earthquakes)
    
    while True:
        schedule.run_pending()
        time.sleep(60)