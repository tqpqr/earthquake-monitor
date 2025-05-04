#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Monolith Script
Handles web scraping, map generation, and Telegram posting for earthquake events.
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from telebot import TeleBot
import os
import logging
from time import sleep

# Import configurations and map functions
try:
    from config import (
        TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID
    )
    from map2 import make_a_map, overlay_a_text
    logger = logging.getLogger(__name__)
    logger.info("Imported configurations and map functions")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import modules: {e}")
    raise

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Define file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COORDINATES_FILE = os.path.join(BASE_DIR, "coordinates.txt")
LAST_EVENT_FILE = os.path.join(BASE_DIR, "last_event.txt")
LAST_MAGNITUDE_FILE = os.path.join(BASE_DIR, "last_magnitude.txt")
MAP_FILE = os.path.join(BASE_DIR, "map.png")
NEW_MAP_FILE = os.path.join(BASE_DIR, "new_map.png")

class ParseMode:
    """Telegram Message Parse Modes."""
    HTML = 'HTML'

def main():
    logger.info("Starting monolith script")
    """Main function to scrape data, generate map, and post to Telegram."""
    driver = None
    try:
        # Read event URL
        logger.info(f"Reading event URL from {LAST_EVENT_FILE}")
        with open(LAST_EVENT_FILE, 'r') as f:
            url = f.read().strip() + '/region-info'

        # Set up Firefox driver
        logger.info("Starting Firefox driver")
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Firefox(options=options)
        logger.info(f"Navigating to {url}")
        driver.get(url)

        # Define XPaths
        mag_n_loc = '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/event-page-header/header/h1'
        time_of_event = "/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/event-page-header/header/ul/li[1]"
        long_lat_path = "/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/event-page-header/header/ul/li[2]"
        depth = "/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/event-page-header/header/ul/li[3]"
        nearby_places = [
            {
                'name': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[1]/geoserve-nearby-place/span',
                'distance': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[1]/geoserve-nearby-place/aside[1]',
                'population': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[1]/geoserve-nearby-place/aside[2]'
            },
            {
                'name': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[2]/geoserve-nearby-place/span',
                'distance': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[2]/geoserve-nearby-place/aside[1]',
                'population': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[2]/geoserve-nearby-place/aside[2]'
            },
            {
                'name': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[3]/geoserve-nearby-place/span',
                'distance': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[3]/geoserve-nearby-place/aside[1]',
                'population': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[3]/geoserve-nearby-place/aside[2]'
            },
            {
                'name': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[4]/geoserve-nearby-place/span',
                'distance': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[4]/geoserve-nearby-place/aside[1]',
                'population': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[4]/geoserve-nearby-place/aside[2]'
            },
            {
                'name': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[5]/geoserve-nearby-place/span',
                'distance': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[5]/geoserve-nearby-place/aside[1]',
                'population': '/html/body/app-root/app-event-page/hazdev-template/div/div/div[2]/main/app-region-info/region-info-display/geoserve-nearby-place-list/div/ol/li[5]/geoserve-nearby-place/aside[2]'
            }
        ]

        # Scrape data
        logger.info("Scraping earthquake data")
        magnitude_and_location = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, mag_n_loc))
        ).get_attribute('innerHTML')
        time_of_event_data = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, time_of_event))
        ).get_attribute('innerHTML')
        long_lat = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, long_lat_path))
        ).get_attribute('innerHTML')
        depth_data = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, depth))
        ).get_attribute('innerHTML')

        nearby_data = []
        for place in nearby_places:
            try:
                city = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH, place['name']))
                ).get_attribute('innerHTML')
                distance = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH, place['distance']))
                ).get_attribute('innerHTML')
                population = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH, place['population']))
                ).get_attribute('innerHTML')
                nearby_data.append({
                    'city': city,
                    'distance': distance,
                    'population': population
                })
            except Exception as e:
                logger.warning(f"Failed to scrape nearby place: {e}")
                continue

        # Read coordinates
        logger.info(f"Reading coordinates from {COORDINATES_FILE}")
        with open(COORDINATES_FILE, 'r') as f:
            long_lat = f.read().strip()

        # Remove old map files
        logger.info("Removing old map files if they exist")
        for map_file in [MAP_FILE, NEW_MAP_FILE]:
            if os.path.exists(map_file):
                try:
                    os.remove(map_file)
                    logger.info(f"Removed {map_file}")
                except Exception as e:
                    logger.warning(f"Failed to remove {map_file}: {str(e)}")

        # Generate map
        logger.info("Generating map")
        response = make_a_map(long_lat, '10,10')
        map_generated = False
        if response:
            with open(MAP_FILE, 'wb') as file:
                file.write(response.content)
            logger.info(f"Map saved as {MAP_FILE}")
            sleep(5)
            if overlay_a_text(magnitude_and_location):
                if os.path.exists(NEW_MAP_FILE):
                    map_generated = True
                else:
                    logger.warning(f"Map file {NEW_MAP_FILE} was not created")
            else:
                logger.warning("Failed to overlay text on map")
        else:
            logger.warning("Map generation failed, proceeding without map")

        # Initialize Telegram bot
        logger.info("Initializing Telegram bot")
        bot = TeleBot(token=TELEGRAM_TOKEN)

        # Read magnitude
        logger.info(f"Reading magnitude from {LAST_MAGNITUDE_FILE}")
        with open(LAST_MAGNITUDE_FILE, 'r') as f:
            magnitude = float(f.read().strip())

        # Prepare message
        nearby_text = ""
        for data in nearby_data:
            city = data['city'].replace("('","").replace("',)","")
            distance = data['distance'].replace("('","").replace("',)","")
            population = data['population'].replace("Population:", "").strip()
            nearby_text += (
                f"<u>Name:</u> <b>{city}</b> \n"
                f"<u>Distance from epicenter:</u> <b>{distance}</b> \n"
                f"<u>Population:</u> <b>{population}</b>\n\n"
            )

        prefix = ""
        if magnitude <= 3.5:
            prefix = ""
        elif magnitude < 5:
            prefix = "<b>! </b>"
        else:
            prefix = "<b>!!! </b>"

        msg = (
            f"{prefix}<b>{magnitude_and_location}</b> \n"
            f"<b>Time: </b> {time_of_event_data} \n"
            f"<b>Depth</b>: {depth_data.replace('depth', '')} \n\n"
            f"<i><b>Nearby settlements: </b></i> \n"
            f"{nearby_text}"
            f"*source: USGS."
        )

        # Send to Telegram
        logger.info(f"Sending message to Telegram channel {TELEGRAM_CHANNEL_ID}")
        if 'undefined' not in magnitude_and_location:
            if map_generated and os.path.exists(NEW_MAP_FILE):
                with open(NEW_MAP_FILE, 'rb') as photo:
                    bot.send_photo(
                        chat_id=TELEGRAM_CHANNEL_ID,
                        photo=photo,
                        caption=msg,
                        parse_mode=ParseMode.HTML
                    )
                logger.info("Message with photo sent successfully")
            else:
                bot.send_message(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    text=msg + "\n<i>Map unavailable due to API error.</i>",
                    parse_mode=ParseMode.HTML
                )
                logger.info("Message sent without photo due to map generation failure")
        else:
            logger.warning("Skipping Telegram message due to invalid magnitude_and_location")

    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        raise
    
    finally:
        if driver:
            logger.info("Closing driver")
            driver.close()
            driver.quit()

if __name__ == "__main__":
    logger.info("Starting monolith script")
    main()
    logger.info("Monolith script completed")