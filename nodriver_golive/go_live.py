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
import re
import random
from bs4 import BeautifulSoup


logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')

#Initialise OCR solver
ocr = ddddocr.DdddOcr()

async def login(page, email, password):
    time.sleep(1)
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
            time.sleep(3)
        else:
            print("Unable to send keys or unable to find the input elements")
    except Exception as e:
        logger.error(e)
        # page.reload()

# <img class="captcha-code" aria-label="captcha image" alt="captcha image" src="data:image/jpeg;charset=utf-8;base64,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">
# <input name="CaptchaCode" class="botdetect-input" tabindex="0" id="solution" type="text" pattern="[A-Za-z0-9]*" aria-label="Enter the code from the picture: ">
# <button class="botdetect-button btn">I'm not a robot</button>
# 
# Check capthca  
async def captcha_solver(page):
    time.sleep(1)
    try:
        captcha_img = await page.query_selector("img[class=captcha-code]")

        if captcha_img:
            logger.info(captcha_img)
            captcha_img_attributes = await captcha_img.get_js_attributes()
            img_src = captcha_img_attributes["src"]
        else:
            logger.error(e)
            
        # solve captcha here
        if img_src.startswith('data:image/jpeg;') or img_src.startswith('data:image/png;'):
            base64_data = img_src.split(",")[1]
            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data))
            image_path = 'downloaded_image.jpg'
            image.save(image_path)

            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            result = ocr.classification(image_bytes)
            logger.info("Solved captcha code: " + result)

            # Clean up the temporary image file
            if os.path.exists(image_path):
                os.remove(image_path)

            # send key
            # <input name="CaptchaCode" class="botdetect-input" tabindex="0" id="solution" type="text" pattern="[A-Za-z0-9]*" aria-label="Enter the code from the picture: ">
            # <button class="botdetect-button btn">I'm not a robot</button>
            input = await page.select("input[class*=botdetect-input]")
            print(input)
            time.sleep(1)
            await input.send_keys(result)

            not_robot_button = await page.select("button[class*=botdetect-button]")
            time.sleep(1)
            await not_robot_button.click()
            # check still have captcha or not            
        else:
            raise ValueError("Image source is not in the expected format")
    except Exception as e:
        logger.error("No captcha image found. Start to check queue status...")

# Check in queue or not
async def is_in_queue(page):
    try:
        while True:
            # Check if the queue text is present
            # in_queue = await page.find_element_by_text("queue")
            select_sections = await page.query_selector("button#popup-avail")
            if not select_sections:
                print("Still in the queue... waiting.")
                await asyncio.sleep(5)  # Wait for 5 seconds before checking again
            else:
                return
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

async def select_sections(page, sections):
    secured = False
    try:
        # Select the map element
        map_div = await page.query_selector("map[name=uMap]")
        print(map_div)
        # Map element shown
        if map_div:
            area = await map_div.query_selector(f"area[href='#fixed.php#{sections}']") 
            print(area)
            # Select s area and click
            if area:
                await area.click()
                print("Section area clicked.")
            else:
                print("Unable to load / find the map.")
    except Exception as e:
        print(f"Error occurred: {e}")


# [<div class="seatuncheck" id="checkseat-N-15" data-seat="N-15-P*698" data-seatk="92c01544ada13c1c36c8f65e267d214b"><span >15</span></div>, 
# <div class="seatuncheck" id="checkseat-R-11" data-seat="R-11-P*698" data-seatk="bf5681e7d6c8d2ecabba1518d2571741"><span >11</span></div>]
async def select_ticket(page, number_of_tickets, allowed_rows, seat_min, seat_max):
    time.sleep(1)
    # check available seats, select seat, randomised
    list_of_unchecked_seats = await page.query_selector_all("div.seatuncheck")
    print(f"List of unchecked seat: {list_of_unchecked_seats}")
    if list_of_unchecked_seats:
        allowed_seats = []
        pattern = re.compile(r'id="checkseat-([A-Z]+)-(\d+)"')
        for i in range(len(list_of_unchecked_seats)):
            this_element = str(list_of_unchecked_seats[i])
            match = pattern.search(this_element)
            print(match)
            if match:
                row, seat = match.group(1), int(match.group(2))
                if row in allowed_rows and seat_min <= seat <= seat_max:
                    allowed_seats.append(list_of_unchecked_seats[i])
        print("Allowed seats: " +  str(allowed_seats))
        if len(allowed_seats):
            chosen_seat = random.choice(allowed_seats)
            await chosen_seat.click()
            # Check if "Close" button popup setting
            # div class="popup popup-content popup-l" id="popup_alert" style="display:none;">
            pop_up = await page.query_selector("div.popup.popup-content.popup-l")
            if pop_up:
                
                soup = BeautifulSoup(pop_up, 'html.parser')
                div_element = soup.find('div', id='popup_alert')
                pop_up_display = div_element.get('style')
                # print("Line174:" + pop_up_display)

                if "none" not in pop_up_display:
                    # Check for "Book Now" button and click 
                    book_now = await page.query_selector("text=Book Now")
                    if book_now:
                        await book_now.click()
                        print("Ticket booked successfully.")
            else:
                close_button = await page.query_selector("button.btn-red.w-auto")
                await close_button.click()
    else:
        print("No seats")