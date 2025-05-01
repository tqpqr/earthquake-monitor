#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map Generation Script
Generates a map with a watermark and text overlay for earthquake locations.
"""

from requests import get
from time import sleep
from PIL import Image, ImageDraw, ImageFont
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import configurations
try:
    from config import (
        YANDEX_MAPS_API, MAP_SCALE, MAP_MARKER, MAP_FILE,
        NEW_MAP_FILE, WATERMARK_FILE, FONT_FILE, FONT_SIZE
    )
    logger.info("Imported configurations from config.py")
except ImportError:
    logger.error("Failed to import config.py")
    raise

def make_a_map(long_lat: str, scale: str, mark: str):
    """
    Fetch a map from Yandex Maps API.
    
    Args:
        long_lat: Longitude and latitude as a comma-separated string
        scale: Map scale (width,height in degrees)
        mark: Marker type
    
    Returns:
        Response object containing the map image
    """
    try:
        logger.debug(f"Fetching map from {YANDEX_MAPS_API}")
        response = get(
            f"{YANDEX_MAPS_API}?ll={long_lat}&lang=en-US&spn={scale}&l=map&pt={long_lat},{mark}"
        )
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code}, {response.text}")
        if not response.headers['Content-Type'].startswith('image'):
            raise Exception(f"Response is not an image: {response.text}")
        logger.debug("Successfully fetched map")
        return response
    except Exception as e:
        logger.error(f"Error fetching map: {e}")
        raise

def overlay_a_text(title: str):
    """
    Overlay text and watermark on the map image.
    
    Args:
        title: Text to overlay on the map
    """
    try:
        logger.debug(f"Opening map image: {MAP_FILE}")
        image = Image.open(MAP_FILE).convert('RGBA')
        logger.debug(f"Opening watermark image: {WATERMARK_FILE}")
        imageWatermark = Image.open(WATERMARK_FILE).convert('RGBA')
        logger.debug(f"Loading font: {FONT_FILE}")
        font = ImageFont.truetype(FONT_FILE, FONT_SIZE)
        drawer = ImageDraw.Draw(image)
        drawer.text(
            (600/2, (450/2)-30),
            f"{title}",
            font=font,
            fill='#ffffff',
            stroke_width=8,
            stroke_fill='#010c80',
            anchor='mm'
        )
        my_img = Image.alpha_composite(image, imageWatermark)
        logger.debug(f"Saving new map image: {NEW_MAP_FILE}")
        my_img.save(NEW_MAP_FILE)
        logger.info(f"Image saved as {NEW_MAP_FILE}")
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise

def main(long_lat: str, title: str):
    """
    Generate and save a map with text and watermark.
    
    Args:
        long_lat: Longitude and latitude as a comma-separated string
        title: Title to overlay on the map
    """
    try:
        # Fetch and save map
        logger.info("Fetching and saving map")
        response = make_a_map(long_lat, MAP_SCALE, MAP_MARKER)
        with open(MAP_FILE, "wb") as file:
            file.write(response.content)
            logger.info(f"Map saved as {MAP_FILE}")
        sleep(1)  # Ensure file write completes
        
        # Overlay text and watermark
        logger.info("Overlaying text and watermark")
        overlay_a_text(title)
        
    except Exception as e:
        logger.error(f"Failed to generate map: {e}")
        raise

if __name__ == "__main__":
    # For testing purposes
    test_long_lat = '-117.8987,38.1577'
    test_title = '57 km west of Nanwalek, Alaska'
    logger.info("Running map2.py in test mode")
    main(test_long_lat, test_title)