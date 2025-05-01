#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Earthquake Monitoring Script
This script fetches the latest earthquake data from USGS and processes it.
"""

import json
import os
import sys
import requests
import subprocess
import logging
import traceback
import schedule
import time
from pathlib import Path
from typing import Tuple, Dict, Any

# Import configurations
try:
    from config import (
        BASE_DIR, USGS_FEED_URL, COORDINATES_FILE, LAST_EVENT_FILE,
        LAST_MAGNITUDE_FILE, ENVIRONMENT
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Imported configurations from config.py: BASE_DIR={BASE_DIR}")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.error("Failed to import config. Using current directory as BASE_DIR.")
    traceback.print_exc()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Log directories
logger.info(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"BASE_DIR: {BASE_DIR}")

# Check if BASE_DIR exists
if not os.path.exists(BASE_DIR):
    logger.error(f"BASE_DIR does not exist: {BASE_DIR}")
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        logger.info(f"Created BASE_DIR: {BASE_DIR}")
    except Exception as e:
        logger.error(f"Failed to create BASE_DIR: {e}")

# Configuration for monolith script
MONOLITH_SCRIPT = os.path.join(BASE_DIR, "monolith.py")

# Log paths
logger.info(f"COORDINATES_FILE: {COORDINATES_FILE}")
logger.info(f"LAST_EVENT_FILE: {LAST_EVENT_FILE}")
logger.info(f"LAST_MAGNITUDE_FILE: {LAST_MAGNITUDE_FILE}")
logger.info(f"MONOLITH_SCRIPT: {MONOLITH_SCRIPT}")

# Check if monolith script exists
if not os.path.exists(MONOLITH_SCRIPT):
    logger.error(f"MONOLITH_SCRIPT does not exist: {MONOLITH_SCRIPT}")
else:
    logger.info(f"MONOLITH_SCRIPT exists: {MONOLITH_SCRIPT}")

def get_last_earthquake(api_url: str) -> Tuple[str, str, float, str, str]:
    """
    Fetch the most recent earthquake data from USGS API.
    """
    try:
        logger.debug(f"Fetching earthquake data from {api_url}")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        quakes = response.json()
        if not quakes.get('features'):
            logger.warning("No earthquake data found in the API response")
            return ("", "", 0.0, "", "")
            
        last_quake = quakes['features'][0]['properties']
        geometry = quakes['features'][0]['geometry']
        
        title = last_quake.get('title', '')
        place = last_quake.get('place', '')
        magnitude = last_quake.get('mag', 0.0)
        url = last_quake.get('url', '')
        
        coordinates = geometry.get('coordinates', [0, 0, 0])[:2]
        coordinates_str = ','.join(str(x) for x in coordinates)
        
        logger.debug(f"Found earthquake: {title}, magnitude: {magnitude}")
        return (title, place, magnitude, url, coordinates_str)
    except requests.RequestException as e:
        logger.error(f"Error fetching earthquake data: {e}")
        return ("", "", 0.0, "", "")
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Error parsing earthquake data: {e}")
        traceback.print_exc()
        return ("", "", 0.0, "", "")

def save_file(file_path: str, content: str) -> None:
    """Save content to a file."""
    try:
        logger.debug(f"Saving content to {file_path}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        logger.debug(f"Successfully saved content to {file_path}")
    except IOError as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        traceback.print_exc()

def read_file(file_path: str) -> str:
    """Read content from a file."""
    try:
        logger.debug(f"Reading from {file_path}")
        if not os.path.exists(file_path):
            logger.warning(f"File does not exist: {file_path}")
            return ""
        with open(file_path, 'r') as f:
            content = f.read().strip()
            logger.debug(f"Successfully read content from {file_path}")
            return content
    except IOError as e:
        logger.error(f"Error reading from file {file_path}: {e}")
        traceback.print_exc()
        return ""

def process_earthquake():
    """Process earthquake data and run monolith script if needed."""
    try:
        # Ensure BASE_DIR exists
        if not os.path.exists(BASE_DIR):
            logger.warning(f"BASE_DIR doesn't exist, creating: {BASE_DIR}")
            os.makedirs(BASE_DIR, exist_ok=True)
        
        # Fetch latest earthquake data
        logger.info("Fetching latest earthquake data")
        title, place, magnitude, url, coordinates = get_last_earthquake(USGS_FEED_URL)
        
        if not url:
            logger.warning("No valid earthquake URL received, exiting")
            return
        
        # Save coordinates
        logger.info("Saving coordinates")
        save_file(COORDINATES_FILE, coordinates)
        
        # Check for new event
        logger.info("Checking if this is a new event")
        last_event_url = read_file(LAST_EVENT_FILE)
        
        if last_event_url == url:
            logger.info("Event already processed, no action needed")
            return
        
        # New event, update files
        logger.info("Processing new event")
        save_file(LAST_EVENT_FILE, url)
        save_file(LAST_MAGNITUDE_FILE, str(magnitude))
        
        # Process the new event
        logger.info(f"Processing new earthquake: {title} (M{magnitude})")
        
        # Run monolith script
        if not os.path.exists(MONOLITH_SCRIPT):
            logger.error(f"Monolith script not found at: {MONOLITH_SCRIPT}")
            try:
                logger.debug(f"Contents of {BASE_DIR}:")
                for item in os.listdir(BASE_DIR):
                    logger.debug(f"  - {item}")
            except Exception as e:
                logger.error(f"Failed to list directory contents: {e}")
            return
            
        python_executable = sys.executable
        logger.info(f"Using Python executable: {python_executable}")
        logger.info(f"Running: {python_executable} {MONOLITH_SCRIPT}")
        
        try:
            process = subprocess.run(
                [python_executable, MONOLITH_SCRIPT],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"Subprocess output: {process.stdout}")
            if process.stderr:
                logger.warning(f"Subprocess errors: {process.stderr}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Subprocess error code: {e.returncode}")
            logger.error(f"Subprocess output: {e.stdout}")
            logger.error(f"Subprocess error: {e.stderr}")
            save_file(LAST_EVENT_FILE, "")
        except FileNotFoundError as e:
            logger.error(f"File not found error when running subprocess: {e}")
            logger.debug(f"Python executable exists: {os.path.exists(python_executable)}")
            logger.debug(f"Script exists: {os.path.exists(MONOLITH_SCRIPT)}")
            
    except Exception as e:
        logger.error(f"Critical error: {e}")
        traceback.print_exc()
        
        if ENVIRONMENT == 'production':
            logger.warning("Rebooting system...")
            # On Railway, we don't reboot; let the restart policy handle it
            raise

def main():
    """Main function to schedule earthquake monitoring."""
    logger.info("Starting earthquake monitoring script")
    
    # Run immediately on start
    process_earthquake()
    
    # Schedule to run every 5 minutes
    schedule.every(5).minutes.do(process_earthquake)
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()