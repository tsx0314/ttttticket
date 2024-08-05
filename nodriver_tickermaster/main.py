import nodriver as uc
import asyncio
import json
import time
from browser_action_ticketmaster import login, click_buy_tickets, find_ticket, select_section,select_ticket_number, best_available, check_captcha, check_box

filename = 'config.json'

with open(filename, 'r') as file:
    config = json.load(file)

print(config)

username = config['username']
print(username)
password = config["password"]
print(password)
url_to_visit = config["url"]
section_data = config["sections"]

# https://ticketmaster.sg/activity/detail/24sg_straykids
last_segment = url_to_visit.split('/')[-1]
print("Last segment taken: " + last_segment)

async def main():
    print("Ticketing starts...")
    browser = await uc.start()
    page = await browser.get(url_to_visit)
    page.set_window_size(0,0,600,900)
    # await login(page, username, password)
    await click_buy_tickets(page,last_segment)
    await find_ticket(page, last_segment)
    await select_section(page,section_data)
    await select_ticket_number(page,2)
    await best_available(page)
    await check_captcha(page)
    await check_box(page) 
    
    time.sleep(1000)
    
if __name__ == '__main__':
    uc.loop().run_until_complete(main())
