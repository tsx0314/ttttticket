import nodriver as uc
import asyncio
import json
import time
from go_live import login, buy_now, ticket_login, select_sections, captcha_solver, is_in_queue, select_ticket

filename = 'config.json'
with open(filename, 'r') as file:
    config = json.load(file)

print(config)

login_url = config["login_url"]
sections = config["sections"]
url = config["event_url"]
e = config["e"]
pw = config["pw"]
allowed_rows = config["allowed_rows"]
seat_min = config["seat_min"] 
seat_max = config["seat_max"]

async def main():
    browser = await uc.start()
    # # check cookies 
    login_page = await browser.get(login_url)

    # # login golive account
    await login(login_page, e, pw)
    time.sleep(2)

    # login golive ticketing account
    ticket_page = await browser.get("https://golive-asia.thaiticketmajor.com/booking/prww/zones.php?query=549")
    await ticket_login(ticket_page,e,pw)
    time.sleep(2)

    # ticketing page hangs need to reload the page 
    # await ticket_page.reload()

    artist_ticket_page = await browser.get("https://golive-asia.thaiticketmajor.com/booking/prww/zones.php?query=587")
    time.sleep(2)

    # go into a queue 
    ##################################################
    await captcha_solver(artist_ticket_page)
    await is_in_queue(artist_ticket_page)
    ##################################################

    # go back to event page and go to ticketing page
    # select the section - the only support one section now
    # await select_sections(artist_ticket_page,sections)
    # time.sleep(1)
    # ticket_secured = False
    # n = 1
    # await select_ticket(artist_ticket_page, n, allowed_rows, seat_min, seat_max)
    # while not ticket_secured:
    #     await select_ticket(artist_ticket_page, n)
    #     await artist_ticket_page.reload()
    #     if (n == 0):
    #         ticket_secured = True

    time.sleep(360000)
    browser.stop()
    
# if __name__ == '__main__':
#     uc.loop().run_until_complete(main())

async def run_multiple_instances(n):
    tasks = [main() for _ in range(n)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    num_instances = 3
    asyncio.run(run_multiple_instances(num_instances))

