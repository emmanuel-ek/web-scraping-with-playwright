from playwright.sync_api import sync_playwright, TimeoutError
from playwright_stealth import stealth_sync
import time
import requests
from playwright.sync_api import expect

class WebHackingBot:
    def __init__(self):
        self.pw = sync_playwright().start()
        self.connection_url = 'wss://browser.zenrows.com?apikey=8d52a81b3ca57cdc829963a7b6b17851e192a30b';  
        # without zenrow
        # self.browser = self.pw.chromium.launch(headless=True)
        # self.context = self.browser.new_context()
        # self.page = self.context.new_page()
        
        # use zenrow    
        self.browser = self.pw.chromium.connect_over_cdp(self.connection_url)
        self.context = self.browser.contexts[0]
        self.page = self.context.new_page()
        
        # apply stealth setttings to the page
        stealth_sync(self.page)
        
        #login credentials
        self.username = "student"
        self.password = "Password1234"
        
        #zenrow credentials
        self.api_key = "8d52a81b3ca57cdc829963a7b6b17851e192a30b"
    
    def capcha_by_pass_with_zenrow(self, page):
        base_url = page
         
        params = {
            "url": base_url,
            "apikey": self.api_key,
            "js_render": "true",
            "premium_proxy": "true",
        }
        
        response = requests.get("https://api.zenrows.com/v1/", params=params)
        
        if response.status_code != 200:
            print("zenrow failed to fetch the page")
            print(response.text)
            return
        
        html = response.text
        print("page extracted successfully with zenrow")
        
        # check zenrows returned page
        self.page.set_content(html)
        returned_page = self.page.locator("h1.post-title", has_text="Contact")
        #self.page.screenshot(path="zenrow_page.png")
        print(f"returned page {returned_page.count()}")
        
    def crawl_on_contact_page(self):
        #contact_page_url = self.page.locator('a', has_text="Contact").get_attribute("href")
        contact_link = self.page.locator('a', has_text="Contact") # get the contact nav link
        if contact_link.count() <= 0:
            print("contact link was not found")
            return
        
        contact_page_url = contact_link.get_attribute("href") # get the url for the contact page
        if contact_page_url is None:
            print("contact page url is not found")
            return
        
        # if the page exists then we can crawl deeper into the contact us page
        self.page.goto(contact_page_url)
        self.page.wait_for_load_state("networkidle")
        #self.page.screenshot(path="test.png")
        
        # try zenrow
        # self.capcha_by_pass_with_zenrow(contact_page_url)
        # return
        
        # let use check if the contact page has been returned
        contact_us_heading = self.page.locator("h1.post-title", has_text="Contact")
        if contact_us_heading.count() <= 0:
            print("contact page is not found")
            return
        
        print("Contact page found successfully")
        
        # obtain the form fields from this page
        first_name_field = self.page.locator("input#wpforms-161-field_0")
        last_name_field = self.page.locator("input#wpforms-161-field_0-last")
        email_field = self.page.locator("input#wpforms-161-field_1")
        comment_field = self.page.locator("textarea#wpforms-161-field_2")
        submit_button = self.page.locator("button#wpforms-submit-161")
        
        print(f"FIRST NAME: {first_name_field}")
        print(f"LAST NAME: {last_name_field}")
        print(f"EMAIL: {email_field}")
        print(f"COMMENT: {comment_field}")
        print(f"SUBMIT BUTTON: {submit_button}")
        
        # let us check if the message exists in the dom initially
        is_message_available = self.page.locator("p", has_text="Thanks for contacting us! We will be in touch with you shortly.")
        if is_message_available.count() <= 0:
            print("The success message is not available in the DOM")
        
        if (
            first_name_field.count() <= 0 or
            last_name_field.count() <= 0 or
            email_field.count() <= 0 or
            comment_field.count() <= 0
        ):
            print(f"some form fields are missing: {first_name_field.count()}")
            return
        
        # fillin the form fields
        first_name_field.fill("John")
        last_name_field.fill("Doe")
        email_field.fill("john@gmail.com")
        comment_field.fill("automation testing with playwright")
    
        # submit the form
        # submit_button.click()  
        # time.sleep(10)
        # we are facing timeout problems while submitting the form
        
        try:
            with self.page.expect_response("**/wpforms*/submit*", timeout=60000) as response_info:
                submit_button.click()
            response = response_info.value
            print(f"Form submission status: {response.status}")
            #print(f"Response body: {await response.json()}")  # For async version
        except TimeoutError:
            print("Form submission timed out - likely blocked by CAPTCHA")
            self.page.screenshot(path="form_submission_timeout.png")
         
        # the success alert is returned by javascript
        # we can use wait_for_load_state to wait until js network finishes
        self.page.wait_for_load_state("networkidle")
        
        # check if the success page have been returned
        # success_message = self.page.locator("p", has_text="Thanks for contacting us! We will be in touch with you shortly.")
        message = "Thanks for contacting us! We will be in touch with you shortly."
        success_message = self.page.get_by_text(message, exact=False)
        #time.sleep(10)
        
        # on fail state
        # if success_message.count() <= 0:
        #     print(f"FAIL: {success_message}")
        #     self.page.screenshot(path="fail_screenshot.png") # take the screenshot
        #     print(f"Sending form failed, with count: {success_message.count()}")
        #     return

        # # on success state
        # self.page.screenshot(path="success_screenshot.png") # take the screenshot
        # print(f"SUCCESS: {success_message}")
        # print("Contact form submitted successfully")
        
        # let us check with the div
        success_div = self.page.locator("div#wpforms-confirmation-161")
        print(f"SUCESS DIV: {success_div.count()}")
        
        try:
            expect(success_message).to_be_visible(timeout=15000)
            self.page.screenshot(path="success_screenshot.png")
            print(f"SUCCESS: {success_message}")
            print("Contact form submitted successfully")
        except Exception as e:
            self.page.screenshot(path="fail_screenshot.png")
            print(f"FAIL: {success_message}")
            print("Sending form failed — success message not visible")
        
        
        # we are being blocked by captcha so we need to implement
        # a Playwright CAPTCHA bypassing logic.
        
        
    def handle_automated_login(self) -> bool:
        # this is a seed url
        self.page.goto("https://practicetestautomation.com/practice-test-login/")
        
        # check if the correct page has been returned
        heading = self.page.locator("h2", has_text="Test login")
        count = heading.count()
        
        if count is None or count <= 0:
            print("wrong page content was returned")
            return False
        
        # check if the page has login field
        username_field = self.page.locator("input#username")
        password_field = self.page.locator("input#password")
        
        if username_field.count() <= 0 or username_field.count() <= 0:
            print("username or password field is not found")
            return False
        
        # fillin the login form
        username_field.fill(self.username)
        password_field.fill(self.password)
        
        submit_button = self.page.locator("button#submit")
        submit_button.click()
        
        # delay for 30 seconds to check if a page has loaded
        try:
            self.page.locator("h1.post-title", has_text="Logged In Successfully").wait_for(timeout=3000)
            print("Login successful.")
            return True
        except:
            print("Login failed. Try using different credentials.")
            # check if he dynamic error div is visible
            # error_message = self.page.locator("div#error", has_text="Your username is invalid!")
            error_message = self.page.locator("div#error")
            if error_message.count() <= 0:
                print("Error message div not is visible")
            else:
                print(f"The error div message is visible {error_message.count()}")
            return False
        
        
if __name__ == "__main__":
    bot = WebHackingBot()
    loggin_status = bot.handle_automated_login()
    
    # crawl on the contact page 
    # and fill in contact form
    if loggin_status:
        bot.crawl_on_contact_page()
    
    # Close the browser at the end
    bot.browser.close()
