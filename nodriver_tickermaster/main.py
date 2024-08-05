import nodriver as uc
import asyncio
import json
import time
from browser_action_ticketmaster import visit_target_website, check_captcha, check_queue, scroll_and_accept, fill_in_ticket_number


filename = 'config.json'

with open(filename, 'r') as file:
    config = json.load(file)

print(config)

url_to_visit = config["url"]
section_data = config["sections"]

url_to_visit

async def main():
    print("Ticketing starts...")
    browser = await uc.start()
    page = await browser.get(url_to_visit)
    page.set_window_size(0,0,600,900)

    time.sleep(1000)
    
if __name__ == '__main__':
    uc.loop().run_until_complete(main())
