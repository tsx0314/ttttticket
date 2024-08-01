import time
from io import BytesIO
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def check_element_exists(browser, xpath):
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return True
    except TimeoutException:
        return False
    
# Click BOOK NOW to enter the waiting room
def book_now(browser, book_now_button_xpath, logger):
    try:
        booknow_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, book_now_button_xpath))
        )
        booknow_button.click()
        logger.info("Found and clicked the 'BOOK NOW' button")
    except TimeoutException as e:
        logger.error("Timeout while waiting for 'BOOK NOW' button.")
        raise e
# Waiting in queue
def is_in_queue(browser,logger):
    queue_text = "You are now in line"
    in_queue = True  # Flag to manage queue status
    
    while in_queue:
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{queue_text}')]"))
            )
            logger.info("Still in queue. Waiting...")

            try:
                modal_button = WebDriverWait(browser, 1).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='buttonConfirmRedirect']"))
                )
                if modal_button.is_displayed() and not modal_button.get_attribute("disabled"):
                    logger.info("Modal pop-up detected. Clicking the 'Accept' button.")
                    modal_button.click()
                    in_queue = False
            except TimeoutException:
                logger.debug("Modal pop-up not present yet.")
            time.sleep(3)
        except TimeoutException:
            logger.info("Not in queue or another issue.")
            in_queue = False

def click_accept(accept_button_xpath, browser, logger):
    try:
        scrollable_div = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ClickToAccept__StyledContent')]"))
        )
        logger.info("Found scrollable div")
        browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        logger.info("Scrolled to bottom of div")
        
        WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, accept_button_xpath))
        ).click()
        logger.info("Clicked 'Accept' successfully")
    except TimeoutException as e:
        logger.error("Timeout while waiting for 'Accept' button: %s", e)
        raise  e
    except Exception as e:
        logger.error("Unable to click 'Accept' button: %s", e)

def set_input_value(confirm_button_xpath, browser, new_value, logger):
    try:
        input_xpath = "//input[@inputmode='numeric']"  
        input_element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, input_xpath))
        )
        input_element.clear()
        input_element.send_keys(str(new_value))
        logger.info(f"Input value set to {new_value}.")

        confirm_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, confirm_button_xpath))
        )
        logger.info("Found the CONFIRM QUANTITY button")
        confirm_button.click()
    except TimeoutException as e:
        logger.error("Timeout while setting input value or clicking confirm button: %s")
        raise e
    except Exception as e:
        logger.error("Error in set_input_value: %s", e)
        raise e

def choose_sections(confirm_seat_button_xpath, browser, section_data, logger):
    if not section_data:
        logger.info("No section data provided.")
        return

    wait = WebDriverWait(browser, 5)
    for section_name in section_data:
        try:
            polygon_xpath = f"//*[name()='polygon' and @data-section-name='{section_name}']"
            try:
                polygon_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, polygon_xpath))
                )
                logger.info(f"Polygon with section name '{section_name}' found")
                browser.execute_script("arguments[0].scrollIntoView(true);", polygon_element)
                polygon_element.click()

                confirm_seat_button = wait.until(
                    EC.presence_of_element_located((By.XPATH, confirm_seat_button_xpath))
                )
                logger.info("Found the CONFIRM SEATS button")
                confirm_seat_button.click()

                # no ticket
                if check_element_exists(browser, "//span[text()='Seats Unavailable']") :
                    button_present = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class,'booking-message-return')]")))
                    button_present.click()
                else: 
                    # //div[contains(@class,"booking-message-header")]
                    # //button[contains(@class,"booking-message-return")]
                    seat_details_element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'StyledSeatDetails')]")))
                    inner_div = seat_details_element.find_element(By.TAG_NAME, 'div')
            
                    inner_text = inner_div.text
                    logger.info(f"Seat selected: {inner_text}")
                    print(f"Inner div text: {inner_text}")
                    # Choose or refresh
                    return
            except TimeoutException as timeout_exception:
                logger.info(f"Polygon with section name '{section_name}' not found or not clickable.")
        except Exception as e:
            logger.error(f"Error with section '{section_name}': {e}")
    logger.info("All sections are grey or unavailable. Refreshing the page.")

def check_out(browser, accept_button_xpath, confirm_button_xpath, confirm_seat_button_xpath, section_data, ticket_number, timeout, logger):
    has_secured = False
    start_time = time.time()
    while not has_secured:
        try:
            # Check if the timeout has been exceeded
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                logger.info("Timeout exceeded. Exiting the checkout process.")
                break
            
            click_accept(accept_button_xpath, browser, logger) 
            set_input_value(confirm_button_xpath, browser, ticket_number, logger)
            choose_sections(confirm_seat_button_xpath, browser, section_data, logger)
            has_secured = True
        except TimeoutException as timeout_exception:
            logger.info("Timeout exception encountered. Refreshing the browser...")
            browser.refresh()
        except Exception as e:
            logger.error("An unexpected error occurred: %s", e)