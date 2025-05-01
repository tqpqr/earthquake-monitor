# Earthquake Monitor

## Overview
Earthquake Monitor is a Python application that tracks recent earthquakes and posts updates to a Telegram channel. It fetches basic earthquake data (magnitude, location, coordinates) from the [USGS Earthquake API](https://earthquake.usgs.gov/fdsnws/event/1/) and uses web scraping to extract additional details (time, depth, nearby settlements) from USGS event pages. The application generates map visualizations and sends them with detailed information to a specified Telegram channel. It runs continuously, checking for new earthquakes at configurable intervals.

### Features
- **Real-time Monitoring**: Checks for new earthquakes every 5 minutes (configurable).
- **Magnitude Filtering**: Processes and publishes only earthquakes above a specified magnitude threshold (default: 4.0).
- **Data Sources**: 
  - Fetches basic metadata (magnitude, location, coordinates, event URL) via the USGS Earthquake API.
  - Extracts detailed information (exact time, depth, nearby settlements with distance and population) by parsing USGS event pages with Selenium, as these data are not available in the API.
- **Map Generation**: Creates map images using API-provided coordinates, with custom text and watermark overlays.
- **Telegram Notifications**: Sends earthquake details and map images to a Telegram channel.
- **Configurable Settings**: Supports customization via environment variables for update frequency, magnitude threshold, and API endpoints.
- **Deployment**: Designed for deployment on Railway with Docker for consistent environments.

## Prerequisites
- **Python**: Version 3.10 or higher.
- **Firefox**: Required for Selenium to parse USGS event pages.
- **geckodriver**: Firefox driver for Selenium.
- **Telegram Bot**: A Telegram bot token and channel ID for notifications.
- **Git**: For version control and deployment.
- **Docker**: For containerized deployment (used on Railway).
- **Railway Account**: For hosting the application (optional).

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/ytqpqr/earthquake-monitor.git
cd earthquake-monitor
```

### 2. Set Up a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
Install the required Python packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Install Firefox and geckodriver (Local Setup)
- **Linux/Mac**:
  - Install Firefox: `sudo apt-get install firefox-esr` (Ubuntu/Debian) or equivalent for your OS.
  - Download `geckodriver` (e.g., [v0.34.0](https://github.com/mozilla/geckodriver/releases)) and add it to PATH:
    ```bash
    wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
    tar -xzf geckodriver-v0.34.0-linux64.tar.gz
    sudo mv geckodriver /usr/local/bin/
    ```
- **Windows**:
  - Install Firefox from the [official website](https://www.mozilla.org/en-US/firefox/new/).
  - Download `geckodriver` and add it to your system PATH.

### 5. Configure Environment Variables
Create a `.env` file in the project root with the following variables:
```plaintext
TELEGRAM_TOKEN=your-telegram-bot-token
TELEGRAM_CHANNEL_ID=@YourChannelID
ENVIRONMENT=production
UPDATE_FREQUENCY_MINUTES=5
MAGNITUDE_THRESHOLD=4.0
USGS_API_URL=https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson
```

- `TELEGRAM_TOKEN`: Obtain from [@BotFather](https://t.me/BotFather) on Telegram.
- `TELEGRAM_CHANNEL_ID`: The ID of the Telegram channel (e.g., `@seismiczone`).
- `UPDATE_FREQUENCY_MINUTES`: How often to check for new earthquakes (default: 5 minutes).
- `MAGNITUDE_THRESHOLD`: Minimum earthquake magnitude to process (default: 4.0).
- `USGS_API_URL`: USGS API endpoint (default fetches earthquakes ≥2.5 for the past 24 hours).

## Project Structure
```
earthquake-monitor/
├── .env                   # Environment variables
├── .gitignore            # Git ignore file
├── config.py             # Configuration loader
├── eq2.py               # Main script for fetching earthquake data via API
├── map2.py              # Helper script for map generation
├── monolith.py          # Script for parsing USGS pages and sending Telegram messages
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration for deployment
├── Procfile             # Railway process configuration
├── watermark15.png      # Watermark image for maps
├── YandexSansDisplay-Regular.ttf  # Font for map annotations
```

## Running Locally
1. Ensure `.env` is configured.
2. Run the main script:
   ```bash
   python eq2.py
   ```
3. The script will:
   - Check for new earthquakes every 5 minutes (or as configured) using the USGS API.
   - Save coordinates, event URL, and magnitude to `coordinates.txt`, `last_event.txt`, and `last_magnitude.txt`.
   - Parse additional details (time, depth, nearby settlements) from USGS event pages using Selenium.
   - Generate a map for new events with magnitude ≥4.0.
   - Post updates to the configured Telegram channel.

## Deploying
1. **Push to GitHub**:
   - Ensure all files are committed and pushed to your GitHub repository.
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Configure Environment Variables**:
   - add:
     ```plaintext
     TELEGRAM_TOKEN=your-telegram-bot-token
     TELEGRAM_CHANNEL_ID=@YourChannelID
     ENVIRONMENT=production
     UPDATE_FREQUENCY_MINUTES=5
     MAGNITUDE_THRESHOLD=4.0
     ```

3. **Monitor Deployment**:
   - Verify that messages are posted to your Telegram channel.

## Configuration
Settings are managed via `config.py` and environment variables:
- **Update Frequency**: Set `UPDATE_FREQUENCY_MINUTES` to change how often the script checks for new earthquakes (e.g., `10` for every 10 minutes).
- **Magnitude Threshold**: Set `MAGNITUDE_THRESHOLD` to filter earthquakes (e.g., `4.5` to process only events ≥4.5).
- **API URL**: Modify `USGS_API_URL` to use a different USGS feed (e.g., `significant_day.geojson` for significant earthquakes).

Example: To check every 10 minutes and only publish earthquakes ≥4.5, update `.env`:
```plaintext
UPDATE_FREQUENCY_MINUTES=10
MAGNITUDE_THRESHOLD=4.5
```

## Why Web Scraping?
The USGS Earthquake API provides basic earthquake metadata (magnitude, location, coordinates, event URL), but lacks detailed information such as exact event time, depth, and nearby settlements (names, distances, populations). To obtain these details, the application uses Selenium to scrape the `/region-info` page of each earthquake event on the USGS website.

## Troubleshooting
- **Selenium Errors**:
  - Ensure `firefox-esr` and `geckodriver` are installed and compatible (e.g., `geckodriver 0.34.0` with Firefox ESR 102+).
  - Check logs for missing libraries and add them to `Dockerfile` if needed (e.g., `libgtk-3-0`).
  - Verify XPath selectors in `monolith.py` match the current USGS website structure.
- **Telegram Issues**:
  - Verify `TELEGRAM_TOKEN` and `TELEGRAM_CHANNEL_ID` are correct.
  - Ensure the bot is added to the channel with posting permissions.
- **Deployment Failures**:
  - Clear Railway build cache by adding `BUILD_ID=1` to variables and removing it after a successful build.
  - Check Railway logs for errors during dependency installation or runtime.
- **API Limitations**:
  - If the USGS API returns incomplete data, verify the `USGS_API_URL` in `.env`.
  - Note that some data (e.g., nearby settlements) are only available via web scraping.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/new-feature`).
3. Commit changes (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a pull request.

## License
This project is licensed under the MIT License.