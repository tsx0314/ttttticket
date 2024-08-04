import nodriver as uc
import asyncio
import time
from browser_action_ticketmaster import visit_target_website, check_captcha, check_queue, scroll_and_accept, fill_in_ticket_number

async def main():
    print("Do something here...")
    browser = await uc.start()
    url_to_visit = 'https://ticketmaster.sg/activity/detail/24sg_zerobaseone'
    page = await browser.get(url_to_visit)

    time.sleep(1000)
    
if __name__ == '__main__':
    uc.loop().run_until_complete(main())
