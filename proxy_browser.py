import nodriver as uc
import ddddocr
import base64
from PIL import Image
from io import BytesIO
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import time
from threading import Thread

# Click BOOK NOW to enter the waiting room
def book_now(browser):
    booknow_button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[div[text()='BOOK NOW']]"))
    )
    booknow_button.click()
    print("Found the BOOKNOW button")

def check_element_exists(browser, class_name):
    try:
        # Wait until the element is present
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )
        # If the above line doesn't raise an exception, the element exists
        return True
    except:
        # If an exception is raised, the element does not exist
        return False
    
# Solving CAPTCHA
def ocr_answer(browser):
    ocr = ddddocr.DdddOcr()
    ocr_img = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//img[@aria-label='captcha image']"))
    )
    img_src = ocr_img.get_attribute("src")

    if img_src.startswith('data:image/jpeg;'):
        base64_data = img_src.split(",")[1]
        image_data = base64.b64decode(base64_data)
        image = Image.open(BytesIO(image_data))
        image_path = 'downloaded_image.jpg'
        image.save(image_path)

        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        result = ocr.classification(image_bytes)
        return result
    else:
        raise ValueError("Image source is not in expected format")

# <img class="captcha-code" aria-label="captcha image" alt="captcha image" src="data:image/jpeg;charset=utf-8;base64,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">
# <input name="CaptchaCode" class="botdetect-input" tabindex="0" id="solution" type="text" pattern="[A-Za-z0-9]*" aria-label="Enter the code from the picture: ">
# <button class="botdetect-button btn">I'm not a robot</button>
    
# Waiting in queue
def is_in_queue(browser):
    queue_text = "You are now in line"
    in_queue = True  # Flag to manage queue status

    # have input or not
    if check_element_exists(browser, "botdetect-input"):
        # have then get ocr value
        ocr_answer = ocr_answer(browser)
        input_element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "botdetect-input"))
        )
        input_element.clear()
        input_element.send_keys(ocr_answer)

        not_robot_button_element = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "botdetect-button btn"))
        )
        # Click the button
        not_robot_button_element.click()

    while in_queue:
        try:
            # Check for the presence of the queue text
            queue_element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{queue_text}')]"))
            )
            print("Still in queue. Waiting...")

            # Check if the modal pop-up is present
            try:
                # Ensure the modal is indeed present
                modal_button = WebDriverWait(browser, 1).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='buttonConfirmRedirect']"))
                )
                
                if modal_button.is_displayed() and not modal_button.get_attribute("disabled"):
                    print("Modal pop-up detected. Clicking the 'Accept' button.")
                    modal_button.click()
                    in_queue = False  # Exit the queue checking loop
                    break
            except Exception as e:
                # Modal button is not present, continue checking the queue
                print(f"Error: {e}")
            time.sleep(3)  # Increase delay to avoid excessive requests
        except Exception as e:
            print(f"Not in queue or another issue: {e}")
            in_queue = False  # Set flag to exit outer loop

def click_accept(accept_button_xpath, browser):
    try:
        # Wait for the scrollable div to be present
        scrollable_div = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ClickToAccept__StyledContent')]"))
        )
        print("Found scrollable div")

        # Debugging: Print the dimensions and scroll information
        # print("Div Size:", browser.execute_script("return arguments[0].getBoundingClientRect();", scrollable_div))
        # print("Scrollable Content Size:", browser.execute_script("return arguments[0].scrollHeight;", scrollable_div))
        # print("Scrollable Div Overflow:", browser.execute_script("return window.getComputedStyle(arguments[0]).overflow;", scrollable_div))

        # Scroll the scrollable div to the bottom
        browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        print("Scrolled to bottom of div")
        
        # Wait for the accept button to be clickable
        WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, accept_button_xpath))
        ).click()
        print("Clicked 'Accept' successfully")
    except Exception as e:
        print(f"Unable to click 'Accept' button: {e}")


def set_input_value(confirm_button_xpath,browser, new_value):
    try:
        # Define the input element with a more specific locator if possible
        input_xpath = "//input[@inputmode='numeric']"  
        wait = WebDriverWait(browser, 10)
        input_element = wait.until(
            EC.presence_of_element_located((By.XPATH, input_xpath))
        )
        
        # Clear the current value and set the new value
        input_element.clear()
        input_element.send_keys(str(new_value))
        print(f"Input value set to {new_value}.")

        # Confirm booking quantity
        confirm_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, confirm_button_xpath))
        )
        print("Found the CONFIRM QUANTITY button")
        confirm_button.click()

    except Exception as e:
        print(f"Error in set_input_value: {e}")

def choose_sections(confirm_seat_button_xpath, browser, section_data):
    if not section_data:
        print("No section data provided.")
        return

    wait = WebDriverWait(browser, 5)

    for section_name in section_data:
        try:
            polygon_xpath = f"//polygon[@data-section-name='{section_name}']"
            try:
                # Wait for the polygon element to be present
                polygon_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, polygon_xpath))
                )
                polygon_element.click()
                print(f"Polygon with section name '{section_name}' found and clicked.")

                confirm_seat_button = wait.until(
                        EC.presence_of_element_located((By.XPATH, confirm_seat_button_xpath))
                    )
                print("Found the CONFIRM SEATS button")
                confirm_seat_button.click()
                
                ###########################################################
                # wait for the next page to load 
                # Check if the seat is taken by looking for an 'x' element
                # click x and continue to search for next section
                # else 
                return 
                ###########################################################
            except TimeoutException:
                print(f"Polygon with section name '{section_name}' not found or not clickable.")
        except Exception as e:
            print(f"Error with section '{section_name}': {e}")
    else:
        # If all sections failed (loop completed without break), refresh the page
        print("All sections are grey or unavailable. Refreshing the page.")
        browser.refresh()