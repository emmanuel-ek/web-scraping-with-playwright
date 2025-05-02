from playwright.sync_api import sync_playwright
import time

class WebHackingBot:
    def __init__(self):
        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=False)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
    
    def handle_automated_login(self):
        self.page.goto("https://practicetestautomation.com/practice-test-login/")
        
        # check if the correct page has been returned
        heading = self.page.locator("h2", has_text="Test login")
        count = heading.count()
        
        if count is None or count <= 0:
            print("wrong page content was returned")
            return
        
        
        # check if the page has login field
        username_field = self.page.locator("input#username")
        password_field = self.page.locator("input#password")
        
        if username_field.count() <= 0 or username_field.count() <= 0:
            print("username or password field is not found")
            return
        
        # fillin the login form
        username_field.fill("student")
        password_field.fill("Password1234")
        
        submit_button = self.page.locator("button#submit")
        submit_button.click()
        
        # delay for 30 seconds to check if a page has loaded
        try:
            self.page.locator("h1.post-title", has_text="Logged In Successfully").wait_for(timeout=3000)
            print("Login successful.")
        except:
            print("Login failed. Try using different credentials.")
            return

        
        self.browser.close()
        
if __name__ == "__main__":
    bot = WebHackingBot()
    bot.handle_automated_login()
