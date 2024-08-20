import nodriver as uc
import asyncio
import json
import time
from go_live import login, buy_now, ticket_login, select_sections

filename = 'config.json'
with open(filename, 'r') as file:
    config = json.load(file)

print(config)

login_url = config["login_url"]
sections = config["sections"]
url = "https://golive-asia.com/event-detail/107/keshi-REQUIEM-TOUR-IN-KUALA-LUMPUR"
e = config["e"]
pw = config["pw"]

async def main():
    browser = await uc.start()
    login_page = await browser.get(login_url)
    time.sleep(5)
    # login golive 
    await login(login_page, e, pw)
    time.sleep(5)
    # event page in golive
    event_page = await browser.get(url,  new_tab=True)
    await buy_now(event_page)
    # go into a queue 
    ##################################################
    # TO DO
    ##################################################
    # thaiticketmaster page login 
    time.sleep(2)
    ticketing_login_page = browser.tabs[-1]
    await ticket_login(ticketing_login_page,e,pw)
    # go back to event page and go to ticketing page 
    time.sleep(2)
    ticketing_page = browser.tabs[1]
    await buy_now(ticketing_page)
    time.sleep(1)
    new_ticketing_page = browser.tabs[-1]
    await select_sections(new_ticketing_page,sections)

    time.sleep(36000)
    
if __name__ == '__main__':
    uc.loop().run_until_complete(main())

