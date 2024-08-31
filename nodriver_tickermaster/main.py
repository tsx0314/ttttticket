import nodriver as uc
import asyncio
import json
import time
from browser_action_ticketmaster import login, click_buy_tickets, find_ticket, select_section,select_ticket_number, best_available, check_captcha, check_box,input_promo_code

filename = 'config.json'

with open(filename, 'r') as file:
    config = json.load(file)

print(config)
promo_code = ""
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
    page = await browser.get("https://ticketmaster.sg")
    page.set_window_size(0,0,600,900)
    
    # await login(page, username, password)

    # login = await page.select("a[href*=login]")
    # await login.click()
    # time.sleep(20)
    # await click_buy_tickets(page,last_segment)
    # await find_ticket(page, last_segment)
    # await input_promo_code(page, promo_code)
    # await select_section(page,section_data)
    # await select_ticket_number(page,2)
    # await best_available(page)
    # await check_captcha(page)
    # await check_box(page) 
    
    time.sleep(36000)
    
# if __name__ == '__main__':
#     uc.loop().run_until_complete(main())

async def run_multiple_instances(n):
    tasks = [main() for _ in range(n)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    num_instances = 2
    asyncio.run(run_multiple_instances(num_instances))
