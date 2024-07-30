import nodriver as uc
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import random
from threading import Thread
from proxy_browser import book_now, is_in_queue, click_accept, set_input_value, choose_sections
from proxy import proxy_chrome

# Load configuration
with open('config.json', 'r') as file:
    config = json.load(file)
# List to keep track of browser instances
browsers = []

# target sections
with open('section.json', 'r') as file:
    section_data = json.load(file)
    print(choose_sections)

# with open('setting.json', 'r') as file:
#     setting_data = json.load(file)
#     print(setting_data)

# Access proxy settings
proxy_host = config['proxy']['host']
proxy_port = config['proxy']['port']
proxy_user = config['proxy']['user']
proxy_pass = config['proxy']['pass']

# Access proxies list
proxy_contents = config['proxies_list']

# Access XPaths
book_now_button_xpath = config['xpaths']['book_now_button']
accept_button_xpath = config['xpaths']['accept_button']
confirm_button_xpath = config['xpaths']['confirm_button']
confirm_seat_button_xpath = config['xpaths']['confirm_seat_button']

# URL to visit
url_to_visit = 'https://my.bookmyshow.com/events/the-boyz-world-tour%3A-zeneration-ii-in-kuala-lumpur/BMSTBOYZ'
ticket_number = 2

def run_proxy_browser():
    [PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS] = random.choice(proxy_contents).split(":")
    try:
        browser = proxy_chrome(PROXY_HOST, int(PROXY_PORT), PROXY_USER, PROXY_PASS)
        browser.get(url_to_visit)
        browsers.append(browser)
        time.sleep(0.5)
       
        while True:
            try:
                print("Attempting to click 'BOOK NOW' button...")
                book_now(browser)
                print("'BOOK NOW' button clicked. Checking queue status...")
                time.sleep(1)
                
                is_in_queue(browser)
                print("Queue status passed. Attempting to click 'Accept' button...")
                while True:
                    try:
                        check_out(browser)
                    except Exception as e:
                        print(f"Time up. Start a new session")

            except Exception as e:
                print(f"Exception occurred: {e}")
                # If button not found, refresh the page
                print("Refreshing page...")
                browser.refresh()
                time.sleep(1)  # Adjust the delay as needed
    except Exception as e:
        print(f"Failed to open browser instance: {e}")

    time.sleep(36000)

def check_out(browser):
    click_accept(accept_button_xpath, browser)
    print("'Accept' button clicked. Setting input value for confirm quantity...")
    set_input_value(confirm_button_xpath, browser, ticket_number)
    choose_sections(confirm_seat_button_xpath, browser, section_data)

def main():
    # Open multiple browser instances
    num_browsers = 1
    threads = []

    for i in range(num_browsers):
        t = Thread(target=run_proxy_browser)
        t.start()
        threads.append(t)
        time.sleep(1)

if __name__ == "__main__":
    main()