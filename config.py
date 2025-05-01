#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration file for the earthquake monitoring system.
"""

import os

# Telegram bot token and channel ID from environment variables
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Validate environment variables
if not TOKEN or not CHANNEL_ID:
    raise ValueError("TELEGRAM_TOKEN and TELEGRAM_CHANNEL_ID must be set in environment variables")

# Base directory for the project (relative path)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Environment setting (development or production)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# API URLs
USGS_FEED_URL = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson'
YANDEX_MAPS_API = 'https://static-maps.yandex.ru/1.x/'

# File paths
COORDINATES_FILE = os.path.join(BASE_DIR, "coordinates.txt")
LAST_EVENT_FILE = os.path.join(BASE_DIR, "last_event.txt")
LAST_MAGNITUDE_FILE = os.path.join(BASE_DIR, "last_magnitude.txt")
MAP_FILE = os.path.join(BASE_DIR, "map.png")
NEW_MAP_FILE = os.path.join(BASE_DIR, "new_map.png")
WATERMARK_FILE = os.path.join(BASE_DIR, "watermark15.png")

# Map settings
MAP_SCALE = '10,10'
MAP_MARKER = 'round'

# Font settings
FONT_FILE = os.path.join(BASE_DIR, "YandexSansDisplay-Regular.ttf")
FONT_SIZE = 24