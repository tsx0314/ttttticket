# main.py
import time
import random
from threading import Thread, Lock
from logger_setup import setup_logging
from config_loader import load_config
from browser_actions import book_now, check_out, is_in_queue
from captcha_solver import solve_captcha
from proxy import proxy_chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def run_proxy_browser(proxy_contents, url_to_visit, book_now_button_xpath, accept_button_xpath, confirm_button_xpath, confirm_seat_button_xpath, captcha_xpath, section_data, ticket_number, lock, logger):
    with lock:
        proxy = random.choice(proxy_contents)

    PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS = proxy.split(":")

    try:
        browser = proxy_chrome(PROXY_HOST, int(PROXY_PORT), PROXY_USER, PROXY_PASS)
        browser.get(url_to_visit)
        logger.info("Browser instance started with proxy: %s", proxy)

        has_secured_ticket = False

        while not has_secured_ticket:
            try:
                logger.info("Attempting to click 'BOOK NOW' button...")
                book_now(browser, book_now_button_xpath, logger)
                logger.info("'BOOK NOW' button clicked. Checking queue status...")
                time.sleep(1)
                solve_captcha(browser, 5, captcha_xpath, logger)
                is_in_queue(browser,logger)
                logger.info("Queue status passed. Attempting to click 'Accept' button...")
                check_out(browser, accept_button_xpath, confirm_button_xpath, confirm_seat_button_xpath, section_data, ticket_number, 600, logger)
                has_secured_ticket = True
                logger.info("Ticket secured. Please finished the check out and payment")
            
            except TimeoutException as e:
                logger.warning("Timeout encountered: %s. Refreshing page...", e)
                browser.refresh()
                time.sleep(1)
            except NoSuchElementException as e:
                logger.error("Element not found: %s. Refreshing page...", e)
                browser.refresh()
                time.sleep(1)
            except Exception as e:
                logger.error("Unexpected error: %s. Refreshing page...", e)
                browser.refresh()
                time.sleep(1)
    except Exception as e:
        logger.error("Failed to open browser instance: %s", e)
    time.sleep(600)
def main():
    logger = setup_logging()

    config = load_config()

    proxy_contents = config['proxies_list']
    url_to_visit = config['url_to_visit']
    ticket_number = config['ticket_number']
    print(ticket_number)
    section_data = config['section_data']

    book_now_button_xpath = config['xpaths']['book_now_button']
    accept_button_xpath = config['xpaths']['accept_button']
    confirm_button_xpath = config['xpaths']['confirm_button']
    confirm_seat_button_xpath = config['xpaths']['confirm_seat_button']
    captcha_xpath = config['xpaths']['captcha_img']

    lock = Lock()
    num_browsers = 1
    threads = []

    for i in range(num_browsers):
        t = Thread(target=run_proxy_browser, args=(proxy_contents, url_to_visit, book_now_button_xpath, accept_button_xpath, confirm_button_xpath, confirm_seat_button_xpath, captcha_xpath, section_data, ticket_number, lock, logger))
        t.start()
        threads.append(t)
        time.sleep(1)
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
