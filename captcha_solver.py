import ddddocr
import os
from PIL import Image
from io import BytesIO
import base64
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

ocr = ddddocr.DdddOcr()

def check_element_exists(browser, class_name):
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )
        return True
    except TimeoutException:
        return False

def ocr_answer(browser, captcha_xpath, logger):
    try:
        ocr_img = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, captcha_xpath))
        )
        img_src = ocr_img.get_attribute("src")

        if img_src.startswith('data:image/jpeg;') or img_src.startswith('data:image/png;'):
            base64_data = img_src.split(",")[1]
            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data))
            image_path = 'downloaded_image.jpg'
            image.save(image_path)

            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            result = ocr.classification(image_bytes)

            # Clean up the temporary image file
            if os.path.exists(image_path):
                os.remove(image_path)

            return result
        else:
            raise ValueError("Image source is not in the expected format")
    except TimeoutException as e:
        logger.error("Timeout while waiting for captcha image: %s", e)
        raise e
    except Exception as e:
        logger.error("Error during OCR processing: %s", e)
        raise e

def solve_captcha(browser, retries, captcha_xpath, logger):
    for attempt in range(retries):
        try:
            if check_element_exists(browser, "botdetect-input"):
                try:
                    ocr_result = ocr_answer(browser, captcha_xpath, logger)
                except Exception as ocr_exception:
                    logger.error("Error during OCR processing: %s", ocr_exception)
                    time.sleep(1)
                    continue

                try:
                    input_element = WebDriverWait(browser, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "botdetect-input"))
                    )
                    input_element.clear()
                    input_element.send_keys(ocr_result)

                    not_robot_button = WebDriverWait(browser, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "botdetect-button.btn"))
                    )
                    not_robot_button.click()
                    time.sleep(1)

                    # Check if CAPTCHA is still present
                    if not check_element_exists(browser, "botdetect-input"):
                        logger.info("CAPTCHA solved successfully.")
                        return
                    else:
                        logger.warning("CAPTCHA solving failed. Retrying...")
                except Exception as e:
                    logger.error("Error during CAPTCHA form submission: %s", e)
                    time.sleep(1)
                    continue
            else:
                logger.info("No CAPTCHA detected.")
                return
        except Exception as e:
            logger.error("Unexpected error during CAPTCHA solving: %s", e)
        time.sleep(2)

    raise Exception("Failed to solve CAPTCHA after multiple attempts.")