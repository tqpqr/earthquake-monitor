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

def make_a_map(long_lat, scale, mark):
    try:
        logger.info(f"Requesting map from Yandex Maps: ll={long_lat}, spn={scale}")
        response = get(f"https://static-maps.yandex.ru/1.x/?ll={long_lat}&lang=en-US&spn={scale}&l=map&pt={long_lat},round,5.5")
        if response.status_code != 200:
            raise Exception(f"Yandex Maps API error: {response.status_code}, {response.text}")
        if not response.headers['Content-Type'].startswith('image'):
            raise Exception(f"Response is not an image: {response.text}")
        logger.info("Map retrieved successfully")
        return response
    except Exception as e:
        logger.error(f"Failed to fetch map: {str(e)}")
        raise

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
    except Exception as e:
        logger.error(f"Failed to process image: {str(e)}")
        raise

def main():
    long_lat = '-117.8987,38.1577'
    title = '57 км к западу от Нанвалека, Аляска'
    scale = '15.5,15.5'
    mark = 'pm2rdm'
    try:
        response = make_a_map(long_lat, scale, mark)
        with open("map.png", "wb") as file:
            file.write(response.content)
            logger.info("Map saved as map.png")
        sleep(1)
        overlay_a_text(title)
        image = Image.open("new_map.png")
        image.show()
        logger.info("Map displayed successfully")
    except Exception as e:
        logger.error(f"Failed to save or display map: {str(e)}")

if __name__ == "__main__":
    main()