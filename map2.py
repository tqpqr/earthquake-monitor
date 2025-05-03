import logging
from requests import get
from time import sleep
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def normalize_coordinates(long_lat):
    """Normalize longitude to [-180, 180] and latitude to [-90, 90]."""
    try:
        lat, lon = map(float, long_lat.split(','))
        lon = ((lon + 180) % 360) - 180  # Normalize longitude
        lat = max(min(lat, 90), -90)     # Clamp latitude
        if abs(lon) >= 179.9 or abs(lat) >= 89.9:
            logger.warning(f"Coordinates {long_lat} are near map boundaries")
        return f"{lat},{lon}"
    except Exception as e:
        logger.error(f"Failed to normalize coordinates {long_lat}: {str(e)}")
        raise

def make_a_map(long_lat, scale, mark):
    try:
        # Normalize coordinates
        normalized_long_lat = normalize_coordinates(long_lat)
        scales = [scale, "5,5", "2,2", "1,1"]  # Try multiple scales
        for current_scale in scales:
            logger.info(f"Requesting map from Yandex Maps: ll={normalized_long_lat}, spn={current_scale}, pt={mark}")
            url = (
                f"https://static-maps.yandex.ru/1.x/?ll={normalized_long_lat}&lang=en-US"
                f"&spn={current_scale}&l=map&pt={normalized_long_lat},{mark}"
            )
            response = get(url)
            if response.status_code == 200:
                if not response.headers['Content-Type'].startswith('image'):
                    raise Exception(f"Response is not an image: {response.text}")
                logger.info("Map retrieved successfully")
                return response
            else:
                logger.warning(f"Yandex Maps API error: {response.status_code}, {response.text}")
                if response.status_code == 400:
                    logger.info(f"Retrying with smaller scale: {current_scale}")
                    continue
                raise Exception(f"Yandex Maps API error: {response.status_code}, {response.text}")
        logger.error("Failed to fetch map after trying all scales")
        return None  # Return None to allow script to continue without map
    except Exception as e:
        logger.error(f"Failed to fetch map: {str(e)}")
        return None

def overlay_a_text(title):
    try:
        logger.info(f"Overlaying text on map: {title}")
        image = Image.open("map.png").convert('RGBA')
        imageWatermark = Image.open("watermark15.png").convert('RGBA')
        font = ImageFont.truetype('YandexSansDisplay-Regular.ttf', 24)
        drawer = ImageDraw.Draw(image)
        drawer.text((600/2, (450/2)-30), f"{title}", font=font, fill='#ffffff', stroke_width=8, stroke_fill='#010c80', anchor='mm')
        my_img = Image.alpha_composite(image, imageWatermark)
        my_img.save('new_map.png')
        logger.info("Map with text and watermark saved as new_map.png")
        return True
    except Exception as e:
        logger.error(f"Failed to process image: {str(e)}")
        return False

def main():
    long_lat = '-117.8987,38.1577'
    title = '57 км к западу от Нанвалека, Аляска'
    scale = '15.5,15.5'
    mark = 'pm2rdm'
    try:
        response = make_a_map(long_lat, scale, mark)
        if response:
            with open("map.png", "wb") as file:
                file.write(response.content)
                logger.info("Map saved as map.png")
            sleep(1)
            if overlay_a_text(title):
                image = Image.open("new_map.png")
                image.show()
                logger.info("Map displayed successfully")
        else:
            logger.warning("Map generation skipped due to API error")
    except Exception as e:
        logger.error(f"Failed to save or display map: {str(e)}")

if __name__ == "__main__":
    main()