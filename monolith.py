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
        TOKEN, CHANNEL_ID, BASE_DIR, COORDINATES_FILE, LAST_EVENT_FILE,
        LAST_MAGNITUDE_FILE, NEW_MAP_FILE
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

class ParseMode:
    """Telegram Message Parse Modes."""
    HTML = 'HTML'

def main():
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
        options.add_argument("--headless=new")
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

        # Generate map
        logger.info("Generating map")
        response = make_a_map(long_lat, '10,10', 'round')
        with open(os.path.join(BASE_DIR, 'map.png'), 'wb') as file:
            file.write(response.content)
        sleep(5)
        overlay_a_text(magnitude_and_location)

        # Initialize Telegram bot
        logger.info("Initializing Telegram bot")
        bot = TeleBot(token=TOKEN)

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
        logger.info(f"Sending message to Telegram channel {CHANNEL_ID}")
        if 'undefined' not in magnitude_and_location:
            with open(NEW_MAP_FILE, 'rb') as photo:
                bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=photo,
                    caption=msg,
                    parse_mode=ParseMode.HTML
                )
            logger.info("Message with photo sent successfully")

    except Exception as e:
        logger.error(f"Critical error: {e}")
        traceback.print_exc()
        os.system('shutdown /r /t 1')
    
    finally:
        if driver:
            logger.info("Closing driver")
            driver.close()
            driver.quit()

if __name__ == "__main__":
    logger.info("Starting monolith script")
    main()
    logger.info("Monolith script completed")