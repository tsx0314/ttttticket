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

# Visit the target url
async def visit_target_website(page):
    logger.info("Finding BOOK NOW button...")
    has_button = False
    while not has_button:
        try: 
            book_now_button = await page.select("button[class*=BookButton__StyledButton]",10)
            print(book_now_button)
            has_button = True
            await book_now_button.click()
            time.sleep(1)
        except TimeoutError as e:
            logger.error("Unable to locate book now button. Start to refresh the browser.")
            page.reload()
        except Exception as e:
            logger.error("Other error: {}. Reload the page.", e)
            page.reload()

# Check capthca  
async def check_captcha(page):
    # <img class="captcha-code" aria-label="captcha image" alt="captcha image" src="data:image/jpeg;charset=utf-8;base64,/9j/4AAQSkZ">
    # <input name="CaptchaCode" class="botdetect-input" tabindex="0" id="solution" type="text" pattern="[A-Za-z0-9]*" aria-label="Enter the code from the picture: ">
    try:
        captcha_img = await page.select("img[class*=captcha]")
        logger.info(captcha_img)
        captcha_img_attributes = await captcha_img.get_js_attributes()
        img_src = captcha_img_attributes["src"]
        
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
            await not_robot_button.click()
            # check still have captcha or not
            # if not habe t
        else:
            raise ValueError("Image source is not in the expected format")
    except Exception as e:
        logger.error("No captcha image found. Checking queue status...")

# Check queue status
async def check_queue(page):
    time.sleep(1)
    in_queue = True 
    while in_queue:
        try:
            # <div id="MainPart_divProgressbar" aria-label="Progress bar" class="progressbar queueElement" data-bind="visible: layout.progressVisible, attr: { 'aria-valuenow':Math.round(ticket.progress() * 100) } " aria-valuemin="0" aria-valuemax="100" role="progressbar" aria-valuenow="100">
            is_still_queue = await page.select("div[id=MainPart_divProgressbar]",3)
            logger.info(is_still_queue)
            logger.info("Still in queue... Please wait...")

            # redirect button
            # <button id="buttonConfirmRedirect" type="button" class="btn" data-bind="click: setActiveClient"><span class="l">Yes, please</span><span class="r">&nbsp;</span></button>
            await redirect(page)
        except TimeoutError as e:
            in_queue = False
            logger.info("Not in queue. Moving to the next step.")
            redirect(page)

# Redirect button
async def redirect(page):
    time.sleep(1)
    try:
        redirect_button = await page.select("button[id*=buttonConfirmRedirect]")
        logger.info("Find redirect button")
        await redirect_button.click()
        logger.info("Redirect button clicked!")
    except TimeoutError as e:
        logger.info("No redirect button detected. Go to the next page.")

# Click accpet button 
async def scroll_and_accept(page):
    # <div class="ClickToAccept__StyledContent-sc-1bm3gjz-3 gJmPMw"><div class="sc-fzpans fcjwmW ClickToAccept__StyledHTMLParser-sc-1bm3gjz-4 dPRNgc bigtix-htmlparser"><ul><li><strong>Please ensure your email address is valid to receive the confirmation email and e-ticket(s). 请确保您的电子邮件地址有效，以便接收确认电子邮件和电子门票。</strong></li></ul><p><br></p><ul><li><strong>Any request of changing email will not be entertained. 任何更改电子邮件的请求將不予受理</strong>。</li></ul><p><br></p><ul><li>Please ensure the ticket category/section that you selected is correct. 请确保您选择的门票类别/区域是正确的。</li></ul><p><br></p><ul><li>There will be no cancellation or changes once transaction is successful. 交易成功后将无法取消或更改。</li></ul><p><br></p><ul><li>Please check on the seats assigned to you at the Booking Summary before check out. 请在付款前检查分配給您的座位。</li></ul><p><br></p></div></div>
    try: 
        scroll_div = await page.find_element_by_text("Please check on the seats assigned to you at the Booking Summary before check out.")
        # await scroll_div.scroll_into_view()
        # <li>Please check on the seats assigned to you at the Booking Summary before check out. 请在付款前检查分配給您的座位。</li>
        # logger.info("Scrolled!")
        # <button type="button" class="sc-AxhUy jbCTDe bigtix-button bigtix-button--primary ClickToAccept__StyledButton-sc-1bm3gjz-2 jUICtK" style=""><div>Accept</div></button>
        accept_button = await page.select("button[class*=ClickToAccept]",2)
        await accept_button.click()
    except Exception as e:
        logger.error(e)

# input ticket quantity
async def confirm_quantity(page):
    try:
        confirm_quatity_button = await page.select("button[id*=booking-next-page]")
        await confirm_quatity_button.click()
    except TimeoutError as e:
        logger.error("Unable to click the confirm quality button.")

async def fill_in_ticket_number(page, ticket_number):
    # <input class="sc-fznWOq egxPGV bigtix-input-number bigtix-input-basic" type="text" inputmode="numeric" min="1" max="Infinity" step="1" value="1">
    # <button type="button" class="sc-AxhUy jbCTDe bigtix-button bigtix-button--primary bigtix-booking-pagenav-next" id="bigtix-booking-next-page" data-test="test-bigtix-booking--pagenav-next" style=""><div>Confirm quantity</div></button>
    try:
        input = await page.select("input[class*=input-number]")
        print(input)
        await input.send_keys(str(ticket_number))
        await confirm_quantity(page)
    except TimeoutError as e:
        logger.error("Unable to detect input for the ticket number!")

# Choose target sections
async def choose_section(page, section_data):
    logger.info("Choosing section...")
    while True:
        for section in section_data:
            try:
                section_id = str(section)
                css_selector = f"rect[id={section_id}]"
                current_section = await page.select(css_selector)
                print(current_section)
                await current_section.mouse_click()
                print("section is clicked.")
                time.sleep(0.5)
                # has redirect to check out page or not
                try:
                    # <button disabled="" aria-disabled="true" type="button" class="sc-AxhUy ifTbUE bigtix-button bigtix-button--primary bigtix-button--disabled bigtix-booking-pagenav-next" id="bigtix-booking-next-page" data-test="test-bigtix-booking--pagenav-next" style="pointer-events: none;"><div>Confirm Seats</div></button>
                    # <button type="button" class="sc-AxhUy ifTbUE bigtix-button bigtix-button--primary bigtix-booking-pagenav-next" id="bigtix-booking-next-page" data-test="test-bigtix-booking--pagenav-next" style=""><div>Confirm Seats</div></button>
                    confirm_seats_button = await page.select("button[id*=booking-next-page]")
                    print(confirm_seats_button)
                    print("confirm seats button found...")

                    ############## BUG HERE ##################
                    button_attributes = await confirm_seats_button.get_js_attributes()
                    ###########################################
                    print(button_attributes)
                    button_style = button_attributes["style"]

                    print(button_style)
                    
                    print("Attributr style is: " + button_style)
                    if "none" in button_style:
                        continue
                    else:
                        await confirm_seats_button.click()  # Click if "none" is not in the button style
                        print("confirm seats button clicked...")

                except Exception as e:
                    logger.error("Line 182: " + e)

                try:
                    # <button type="button" class="sc-AxhUy ifTbUE bigtix-button bigtix-button--primary bigtix-booking-message-return"><div>Back</div></button>
                    await page.find_element_by_text("Seats Unavailable")
                    # <button type="button" class="sc-AxhUy ifTbUE bigtix-button bigtix-button--secondary bigtix-booking-pagenav-back" id="bigtix-booking-prev-page" data-test="test-bigtix-booking--pagenav-back"><div>Back</div></button>
                    back_button = await page.selector("button[class*=booking-message-return]")
                    await back_button.click()
                except Exception as e:
                    logger.info("No 'Unavaiable' sign found. Continue...")

                try:
                    # <button type="button" class="sc-fzoiQi hEJeAX bigtix-button bigtix-button--primary bigtix-booking-pagenav-next" id="bigtix-booking-next-page" data-test="test-bigtix-booking--pagenav-next"><div>Checkout</div></button>
                    checkout_button = await page.find_element_by_text("Checkout")
                    checkout_button.click()
                except Exception as e:
                    logger.info("Unable to check out, continue to the next section")
                    continue
                print("Ticket secured. Please proceed to check out.")
                return  # Exit the function if seats are successfully confirmed
            except TimeoutError as e:
                logger.warning(f"TimeoutError while trying to click section {section}: {e}")
            except Exception as e:
                logger.error(f"An error occurred while selecting section {section}: {e}")
        logger.error("Unable to select any section from the provided section_data.")
        time.sleep(10)
        page.reload(False)
