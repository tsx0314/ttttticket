import nodriver as uc
import asyncio
import time
from nodriver_browser_action import visit_target_website, check_captcha, check_queue, scroll_and_accept, fill_in_ticket_number, choose_section
import json

filename = 'config.json'

with open(filename, 'r') as file:
    config = json.load(file)

print(config)

url_to_visit = config["url"]
section_data = config["sections"]

async def main():
    browser = await uc.start()
    page = await browser.get(url_to_visit)
    # Set the window size to avoid the scroll accept
    await page.set_window_size(left=0, top=0, width=600, height=900)

    await visit_target_website(page)
    await check_captcha(page)
    time.sleep(1)
    await check_queue(page)
    await scroll_and_accept(page)
    await fill_in_ticket_number(page, 2)
    await choose_section(page, section_data)
    time.sleep(1000)
    
if __name__ == '__main__':
    uc.loop().run_until_complete(main())
