import nodriver as uc
import asyncio
import time
import base64
from io import BytesIO
from cap_solver import captcha

isSolving = True

async def signin(page):
    try:
        field_email = await page.query_selector("input[id=email]")
        field_pwd= await page.query_selector("input[id=pwd]")
        confirm_button = await page.query_selector('a[id=formSubmit]')

        if field_email and field_pwd and confirm_button:
            await field_email.send_keys(EMAIL)
            await field_pwd.send_keys(PASSWORD)
            await confirm_button.click()
        else:
            print("Failed to locate one or more fields on the page.")
    except Exception as e:
        print("Error during signin:", e)


async def select_date(page):
    try:
        date = await page.find(DATE, best_match=True)
        if date:
            await date.click()
        else:
            print("Failed to locate date column.")
        get_ticket = await page.query_selector('button[data-prodtypecode=PT0001]')
        time.sleep(0.5)
        if get_ticket:
            await get_ticket.mouse_click()
        else:
            print("Failed to locate the GetTickets button.")
    except Exception as e:
        print("Error during select_date:", e)
                    
async def captcha_solver(page):
    
    try:
        cap_img = await page.query_selector("img[id=captchaImg]")
        if not cap_img:
            print("Unable to get captcha image element.")
            return
        else:
            print(cap_img)
            img_attributes = await cap_img.get_js_attributes()
            img_src = img_attributes['src']
            print(img_src)
            if img_src and img_src.startswith(('data:image/jpeg;', 'data:image/png;')):
                base64_data = img_src.split(",")[1]
                image_data = base64.b64decode(base64_data)
                image = Image.open(BytesIO(image_data))
                image.save("captcha.png")
            else:
                print("No base64 image found or unsupported format.")
                return

            res = captcha("captcha.png")  
            if res:
                input_box = await page.query_selector("input[class=placeholder]")
                if input_box:
                    await input_box.type(res)
                    complete_button = await page.find('Submit',best_match=True)
                    if complete_button:
                        await complete_button.click()
                else:
                    print("Captcha input box not found.")
    except Exception as e:
        print("Error during captcha_solver:", e)


async def main():
    browser = await uc.start()
    page = await browser.get(LOGIN_LINK)
    await asyncio.sleep(2)
    
    await signin(page)
    await asyncio.sleep(1)

    ticket_page = await browser.get(TICKET_LINK)
    await select_date(ticket_page)
    await asyncio.sleep(5)

  
    print("Waiting for new page to open...")
    while len(browser.tabs) < 2:
        await asyncio.sleep(0.2)  # Small delay to avoid busy-wait

    new_page = browser.tabs[1]
    print("New page detected. Solving CAPTCHA...")
    await asyncio.sleep(0.5)
    await captcha_solver(new_page)

    # global isSolving
    # while(isSolving):
    #     # <button type="button" class="reflash" id="btnReload">Re Flash</button>
    #     await captcha_solver(page)
    #     # if donthasthis:
    #     #     isSolving = False

    await asyncio.sleep(10000) 

if __name__ == '__main__':
    try:
        uc.loop().run_until_complete(main())
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt. Exiting gracefully.")
