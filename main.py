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


# Proxy credentials and other settings
PROXY_HOST = 'gate.smartproxy.com'
PROXY_PORT = 7000
PROXY_USER = 'spx4zk5nx7'
PROXY_PASS = '5_jke0RD5ztbwue5XW'

# Define your proxies list
proxy_contents = [
    "gate.smartproxy.com:7000:spx4zk5nx7:5_jke0RD5ztbwue5XW"
]

# List to keep track of browser instances
browsers = []

# button path
booknow_button_xpath = "//button[div[text()='BOOK NOW']]"
accept_button_xpath = "//button[div[text()='Accept']]"
confirm_button_xpath = "//button[div[translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')='CONFIRM QUANTITY']]"
confirm_seat_button_xpath = "//button[div[translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')='CONFIRM SEATS']]"

# target sections
with open('section.json', 'r') as file:
    data = json.load(file)
    print(data)

with open('setting.json', 'r') as file:
    setting_data = json.load(file)
    print(setting_data)

# URL to visit
url_to_visit = 'https://my.bookmyshow.com/events/the-boyz-world-tour%3A-zeneration-ii-in-kuala-lumpur/BMSTBOYZ'

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
    set_input_value(confirm_button_xpath, browser, 2)
    section_name = 'ZONE B'
    print(f"Choosing section {section_name}...")
    choose_sections(confirm_seat_button_xpath, browser, section_name)
    print("Section chosen. Exiting loop.")

def main():
    # Open multiple browser instances
    num_browsers = 1
    threads = []

    for i in range(num_browsers):
        t = Thread(target=run_proxy_browser)
        t.start()
        threads.append(t)
        time.sleep(1)

    # Wait for all threads to complete
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()