from playwright.sync_api import sync_playwright
import time

class WebHackingBot:
    def __init__(self):
        self.pw = sync_playwright().start()  
        self.browser = self.pw.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        
        #login credentials
        self.username = "student"
        self.password = "Password123"
    
    def crawl_on_contact_page(self):
        contact_page_url = self.page.locator('a', has_text="Contact").get_attribute("href")
        if contact_page_url.count() <= 0:
            print("contact page not found")
            return  
        
        # This function will handle custom page filling
        # by passing some captcha
        # and submittig the form
        print(f"Contact Page URL: {contact_page_url}")        
    
    def handle_automated_login(self) -> bool:
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
