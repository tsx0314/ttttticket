import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import ddddocr
import requests
from PIL import Image
from io import BytesIO
import time
import logging.config

filename = 'logging.conf'
if os.path.exists(filename):
    logging.config.fileConfig(filename)
    logger = logging.getLogger('myLogger')
else:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('defaultLogger')
    logger.warning('logging.conf not found, using default logging configuration')


#Initialise OCR solver
ocr = ddddocr.DdddOcr()

async def login(page, username, password):
    try:
        login = await page.select("a[href*=login]")
        await login.click()
        # <input id="signInFormUsername" name="username" type="text" class="form-control inputField-customizable" placeholder="name@host.com" autocapitalize="none" required="" value="">
        # <input id="signInFormPassword" name="password" type="password" class="form-control inputField-customizable" placeholder="Password" required="">
        # <input name="signInSubmitButton" type="Submit" value="Sign in" class="btn btn-primary submitButton-customizable" aria-label="submit">
        
        # <input id="signInFormUsername" name="username" type="text" class="form-control inputField-customizable" placeholder="name@host.com" autocapitalize="none" required="" value="">
        ################    BUG TO FIX  ##########################
        try:
            account_field = await page.query_selector('input[type=text]')
            if account_field:
                print("Account input found: " + account_field)
                await account_field.send_keys("tian.shixing2001@gmail.com")
                time.sleep(1)
            else:
                print("account input not found")
        except Exception as e:
            print("send_keys fail for username.")
            print(e)
            
        try:
            password_selector = 'input[type~=password]'
            password_field= await page.query_selector(password_selector)
            if password_field:
                print("Password input found: " + password_field)
                await password_field.send_keys(password)
                time.sleep(1)
            else:
                print("password input not found.")
        except Exception as e:
            print("send_keys failed for password. ")
            print(e)

        try:
            submit = await page.query_selector_all("input[type*=Submit]")
            if submit:
                await submit[0].click()
            else:
                logger.error("Unable to find submit button")
        except Exception as e:
            logger.error("Failed to click the button: " + e)
    except TimeoutError as e:
        print(e)

# <a class="btn btn-primary btn-block btn-findTickets nav-ticket" href="/activity/game/24sg_zerobaseone" rel="nofollow">BUY TICKETS</a>
# <a class="btn btn-primary text-bold m-0" href="https://ticketmaster.sg/ticket/area/24sg_txt/1719" rel="nofollow" data-href="https://ticketmaster.sg/ticket/area/24sg_txt/1719">Find tickets</a>


async def click_buy_tickets(page,url_seg):
    print("start 'Click and buy'")
    # <a class="btn btn-primary btn-block btn-findTickets nav-ticket" href="/activity/game/24sg_zerobaseone" rel="nofollow">BUY TICKETS</a>
    try:
        ticket_button_selector = 'a.btn.btn-primary.btn-block.btn-findTickets.nav-ticket'
        buy_tickets_button = await page.query_selector(ticket_button_selector)
        if buy_tickets_button:
            print(buy_tickets_button)
            await buy_tickets_button.click()
        else:
            logger.error("Unable to find  'But tickets' button")
    except Exception as e:
        logger.error(e)

# <a class="btn btn-primary text-bold m-0" href="https://ticketmaster.sg/ticket/area/24sg_straykids/1778" rel="nofollow" data-href="https://ticketmaster.sg/ticket/area/24sg_straykids/1778">Find tickets</a>
async def find_ticket(page, url_seg):
    print("start 'find ticket'")
    time.sleep(1)
    try:
        find_button_selector = "a.btn.btn-primary.text-bold.m-0"
        find_ticket_button = await page.select(find_button_selector)
        if find_ticket_button:
            print(find_ticket_button)
            await find_ticket_button.click()
        else:
            logger.error("Unable to find 'Find Tickets' button")
    except TimeoutError as e:
        logger.error(e)
        page.reload()

async def input_promo_code(page, promo_code):
    # <input type="text" id="checkCode" class="promoCodeInput" name="checkCode" onkeypress="if (event.keyCode == 13) {$(&quot;.check-discount&quot;).trigger(&quot;click&quot;);}">
    try:
        input_field = await page.query_selector("input#checkCode.promoCodeInput")
        if input_field:
            await input_field.click()
            await input_field.send_keys(promo_code)
            print("Promo code sent!")
        else:
            logger.error("Unable to locate input field")
        selector = "button.btn.btn-primary.btn-sm.check-discount"
        submit_button = await page.query_selector(selector)
        if submit_button:
            await submit_button.click()
            time.sleep(1)
        else:
            logger.error("Unable to locate submit button")
    except Exception as e:
        logger.error(e)

async def select_section(page,section):
   # <g id="field_PEND_VIP" class="empty">
	# 	<g>
	# 		<polygon fill="#b9e7df" points="439.4,283.6 438.1,275.1 562.2,342.2 563.4,350.7 			"></polygon>
	# 	</g>
	# 	<g>
	# 		<polygon fill="#b9e7df" points="561.9,342.4 563,350.2 439.7,283.4 438.5,275.6 			"></polygon>
	# 	</g>
	# 	<g>
	# 		<polygon fill="#bcede5" points="561.6,342.3 595.5,318.5 596.7,327 562.8,350.7 			"></polygon>
	# 	</g>
	# 	<g>
	# 		<polygon fill="#bcede5" points="595.3,319 596.4,326.9 563,350.2 561.9,342.4 			"></polygon>
	# 	</g>
	# 	<g>
	# 		<polygon fill="#bdeee6" points="438,275.6 471.9,251.9 595.8,319 561.9,342.7 			"></polygon>
	# 	</g>
	# 	<g>
	# 		<polygon fill="#bdeee6" points="471.9,252.2 595.3,319 561.9,342.4 438.5,275.6 			"></polygon>
	# 	</g>
	# </g>
    try: 
        section_css_selector = "#field_318"
        section_element = await page.query_selector(section_css_selector)
        if section_element:
            print(section_element)
            time.sleep(1)
            await section_element.click()
    except Exception as e:
        logger.error(e)
        
async def select_ticket_number(page, nubmer):
    # <select id="TicketForm_ticketPrice_003" class="w100 form-select" name="TicketForm[ticketPrice][003]">
    try:
        select_element = await page.select("select[id*=TicketForm_ticketPrice]")
        await select_element.send_keys(nubmer)
    except Exception as e:
        logger.error(e)

async def best_available(page):
    # <button type="button" id="autoMode" class="btn btn-primary">Best Available</button>
    try:
        best_available_button = await page.find_element_by_text("Best Available")
        await best_available_button.click()
    except Exception as e:
        logger.error(e)


async def check_captcha(page):
    # <img id="TicketForm_verifyCode-image" src="/ticket/captcha?v=66b0a4597a07e0.23610135" alt="" style="cursor:pointer;">
    try:
        check_captcha_img = await page.select("img[id*=TicketForm_verifyCode-image]")
        img_attribute = await check_captcha_img.get_js_attributes()
        img_url = "https://ticketmaster.sg/ticket" + img_attribute['src']
        print(img_url)

        img_response = requests.get(img_url)
        img = Image.open(BytesIO(img_response.content))
        img.save('captcha_image.png')
        print("CAPTCHA image saved as 'captcha_image.png'")

        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        ocr_result = ocr.classification(img_bytes)
        print("Result: " + ocr_result)
        time.sleep(1)
        # <input type="text" id="TicketForm_verifyCode" class="" name="TicketForm[verifyCode]" placeholder="Verification Code">
        captcha_input = await page.select("input[id=TicketForm_verifyCode]")
        await captcha_input.send_keys(ocr_result)
        
    except Exception as e:
        logger.error(e)


async def check_box(page):
    try:
        # <input type="checkbox" id="TicketForm_agree" class="form-check-input" name="TicketForm[agree]" value="1" data-gtm-form-interact-field-id="0">
        # <button type="submit" class="btn btn-primary">Submit</button>
        check_box_element = await page.select("input[type=checkbox]")
        submit_button = await page.select("button[type=submit]")

        await check_box_element.click()
        time.sleep(0.5)
        await submit_button.click()
    except Exception as e:
        logger.error(e)
