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
            # click
        else:
            raise ValueError("Image source is not in the expected format")
    except Exception as e:
        logger.error("No captcha image found. Checking queue status...")

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

async def redirect(page):
    time.sleep(1)
    try:
        redirect_button = await page.select("button[id*=buttonConfirmRedirect]")
        logger.info("Find redirect button")
        await redirect_button.click()
        logger.info("Redirect button clicked!")
    except TimeoutError as e:
        logger.info("No redirect button detected. Go to the next page.")

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

# <g id="layer-overview">
#     <rect class="cls-1" x="106.9" y="135.8" width="1080" height="1459.9"></rect>
#     <polygon id="area-01" link="ZONE A (L).svg" class="cls-2 bigtix-overview-map__area bigtix-overview-map__area-hidden" points="257.2 679.7 338.3 680.4 427.9 681.3 474.3 681.3 474.3 615.9 257.2 615.9 257.2 679.7" data-category="01" data-section-name="ZONE A (L)" data-section-id="c09f2ca5-52a5-4c72-85a3-b9863735bc9a" data-area-code="01"></polygon>
#     <polygon id="area-02" link="ZONE A (R).svg" class="cls-2 bigtix-overview-map__area bigtix-overview-map__area-hidden" points="814.3 680.7 733.2 681.4 643.6 681.3 597.2 681.3 597.2 615.9 814.3 615.9 814.3 680.7" data-category="10" data-section-name="ZONE A (R)" data-section-id="1b29a8b0-08cc-4ee5-bb63-747ce4345182" data-area-code="02"></polygon>
#     <polygon id="area-03" link="ZONE B.svg" class="cls-2 bigtix-overview-map__area bigtix-overview-map__area-hidden" points="734.8 688.5 644.2 688.1 597.1 689.1 596.8 729.1 535.7 729.2 474.7 729.1 474.4 688.1 427.3 688.1 336.6 687.5 257 687 257.5 723.8 257.5 762.8 525.6 762.8 545.9 762.8 814 762.8 814 723.8 814.5 688 734.8 688.5" data-category="02" data-section-name="ZONE B" data-section-id="7c76ae11-0c27-42fa-941a-94cc77fd70c4" data-area-code="03"></polygon>
#     <rect id="area-04" class="cls-2 bigtix-overview-map__area" x="257" y="769" width="266.5" height="114.2" data-category="03" data-section-name="ZONE C (L)" data-area-code="04"></rect>
#     <rect id="area-05" class="cls-2 bigtix-overview-map__area" x="540.5" y="769" width="274" height="114.2" data-category="07" data-section-name="ZONE C (R)" data-area-code="05"></rect>
#     <rect id="area-06" link="P1(L).svg" class="cls-2 bigtix-overview-map__area" x="257.1" y="961.8" width="164.1" height="100.5" data-category="04" data-section-name="P1 (L)" data-section-id="2d7f6ad5-be4b-4c2e-a5ce-8b138f3dea0c" data-area-code="06"></rect>
#     <polygon id="area-07" link="P1(C).svg" class="cls-2 bigtix-overview-map__area bigtix-overview-map__area-hidden" points="567.6 961.8 567.6 1037.7 505.7 1037.7 505.7 961.8 432.3 961.8 432.3 1062.3 638.4 1062.3 638.4 961.8 567.6 961.8" data-category="04" data-section-name="P1 (C)" data-section-id="da09bad0-13d9-4f60-b362-6bdbb98fa240" data-area-code="07"></polygon>
#     <rect id="area-08" link="P1(R).svg" class="cls-2 bigtix-overview-map__area" x="649.1" y="961.8" width="166.2" height="100.5" data-category="04" data-section-name="P1 (R)" data-section-id="28282cb8-4889-4e97-ae83-889cc22ced3c" data-area-code="08"></rect>
#     <rect id="area-09" link="P2(L).svg" class="cls-2 bigtix-overview-map__area bigtix-overview-map__area-hidden" x="257.1" y="1074.4" width="164.1" height="87.8" data-category="05" data-section-name="P2 (L)" data-section-id="d6c84457-ff9c-4098-a015-990b0f87cb80" data-area-code="09"></rect>
#     <rect id="area-10" link="P2(C).svg" class="cls-2 bigtix-overview-map__area bigtix-overview-map__area-hidden" x="431.4" y="1074.4" width="206.1" height="173.8" data-category="05" data-section-name="P2 (C)" data-section-id="88026a6a-6f9d-42c0-a744-e1146583055b" data-area-code="10"></rect>
#     <rect id="area-11" link="P2 (R).svg" class="cls-2 bigtix-overview-map__area bigtix-overview-map__area-hidden" x="649.1" y="1074.4" width="166.2" height="87.8" data-category="05" data-section-name="P2 (R)" data-section-id="e9326021-5ccb-4a21-a0d5-9686830c8d84" data-area-code="11"></rect>
#     <rect id="area-12" link="P3(L).svg" class="cls-2 bigtix-overview-map__area bigtix-overview-map__area-hidden" x="257.1" y="1174.1" width="164.1" height="74" data-category="06" data-section-name="P3 (L)" data-section-id="94fde3af-025b-4e6e-8c2f-f8c68ac58edc" data-area-code="12"></rect>
#     <rect id="area-13" link="P3 (R).svg" class="cls-2 bigtix-overview-map__area bigtix-overview-map__area-hidden" x="649.1" y="1174.1" width="166.2" height="74" data-category="06" data-section-name="P3 (R)" data-section-id="9bc4ddb3-11d6-43a8-8766-478e89576be6" data-area-code="13"></rect>
#     <rect id="area-14" class="cls-1 bigtix-overview-map__area bigtix-overview-map__area-hidden" x="461.2" y="898.3" width="37.3" height="26.6" data-category="08" data-section-name="P1 Special Need" data-area-code="14"></rect>
#     <rect id="area-15" class="cls-1 bigtix-overview-map__area bigtix-overview-map__area-hidden" x="250.5" y="563.2" width="68.3" height="34.3" data-category="09" data-section-name="Without Seat" data-area-code="15"></rect>
#   </g>

async def choose_section(page, section_data):
    logger.info("Choose section...")
    for section in section_data:
        try:
            css_selector = "rect[id*=area-05]"
            current_section = await page.select(css_selector)
            # print(current_section)
            await current_section.scroll_into_view()
            await current_section.mouse_click()
            # <button disabled="" aria-disabled="true" type="button" class="sc-AxhUy ifTbUE bigtix-button bigtix-button--primary bigtix-button--disabled bigtix-booking-pagenav-next" id="bigtix-booking-next-page" data-test="test-bigtix-booking--pagenav-next" style="pointer-events: none;"><div>Confirm Seats</div></button>
            time.sleep(0.5)
            confirm_seats_button = await page.select("button[id*=booking-next-page]")
            try:
                is_clickable = await confirm_seats_button.get_js_attributes("aria-disabled")
            except Exception as e:
                logger.info("Clickable")
            await confirm_seats_button.click()
            logger.info("Click!!!!!!!!!!!!!!")
            return  # Exit the function if seats are successfully confirmed
        except TimeoutError as e:
            logger.warning(f"TimeoutError while trying to click section {section}: {e}")
            continue
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            continue  # Move to the next section if there's a general error

    logger.error("Unable to select any section from the provided section_data.")

        