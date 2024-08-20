import os
import nodriver as uc
import asyncio
import time
import logging
import ddddocr
import base64
from PIL import Image
from io import BytesIO
import logging.config
# Load logging configuration file
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')

#Initialise OCR solver
ocr = ddddocr.DdddOcr()

async def login(page, email, password):
    try: 
        e_input = await page.query_selector("input[placeholder=Email]")
        pw_input = await page.query_selector("input[placeholder=Password]")
        login = await page.query_selector("button.w-full.rounded.text-center.text-sm.font-bold.text-golive.p-3.bg-black.hover\:bg-gray-800")
        if e_input and pw_input and login:
            await e_input.send_keys(email)
            await pw_input.send_keys(password)
            await login.click()
        else:
            print("Unable to send keys or unable to find the input elements")
    except Exception as e:
        logger.error(e)
        page.reload()

async def buy_now(page):
    time.sleep(2)
    try:
        buy = await page.find_elements_by_text("Buy Now")
        await buy[0].click()
    except Exception as e:
        logger.error(e)

async def ticket_login(page,email,password):
    time.sleep(2)
    print(page)
    # 
    # <input id="signInFormUsername" name="username" type="text" class="form-control inputField-customizable" placeholder="name@host.com" autocapitalize="none" required="" value="">
    # <input id="signInFormPassword" name="password" type="password" class="form-control inputField-customizable" placeholder="Password" required="">
    # <input name="signInSubmitButton" type="Submit" value="Sign in" class="btn btn-primary submitButton-customizable" aria-label="submit">
    try: 
        div_desktop = await page.query_selector("div.modal-content-desktop.visible-md.visible-lg")
        e_input = await div_desktop.query_selector("input[id=signInFormUsername]")
        pw_input = await div_desktop.query_selector("input[id=signInFormPassword]")
        sign_in = await div_desktop.query_selector("input[name=signInSubmitButton]")
        if e_input and pw_input and sign_in:
            await e_input.send_keys(email)
            await pw_input.send_keys(password)
            time.sleep(1)
            await sign_in.click()
        else:
            print("Unable to send keys or unable to find the input elements")
    except Exception as e:
        logger.error(e)
        # page.reload()

# async def 
# <img class="captcha-code" aria-label="captcha image" alt="captcha image" src="data:image/jpeg;charset=utf-8;base64,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">
# <input name="CaptchaCode" class="botdetect-input" tabindex="0" id="solution" type="text" pattern="[A-Za-z0-9]*" aria-label="Enter the code from the picture: ">
# <button class="botdetect-button btn">I'm not a robot</button>


async def select_sections(page, sections):
    # css - uMap32
    try:
        map_div = await page.select("map[name=uMap]",timeout=10)
        print(map_div)
        if map_div:
            for s in sections:
                # <area shape="poly" coords="376,158,422,157,427,224,378,224" href="#fixed.php#306" onclick="selectzone(this.href, event)">
                area = await map_div.query_selector(f"area[href='#fixed.php#{s}']")
                print(area)
                if area:
                    await area.click()
                    time.sleep(2)
                    await select_seat(page)
                else:
                    print("Unable to load / find the area: " + (str)s)
        else:
            print("Unable to load / find the map.")
    except Exception as e:
        logger.error(e)


async def select_seat(page):
    # unchecked seat 
    # <div class="seatuncheck" id="checkseat-H-22" data-seat="H-22-P*688" data-seatk="a5cf1689ec8ca7a9d2472e746e66d1e9"><span>22</span></div>
    try:
        list_of_unchecked_seats = await page.query_selector_all("div[class=seatuncheck]")
        print(len(list_of_unchecked_seats))
        for i in range(len(list_of_unchecked_seats)):  # Use -1 to avoid IndexError for the last item
            current_seat = list_of_unchecked_seats[i]
            await current_seat.click()
            book_now = await page.find_elements_by_text("Book Now")
            await book_now.click()
    except Exception as e:
        logger.error(e)

