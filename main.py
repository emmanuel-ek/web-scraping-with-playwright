from playwright.sync_api import sync_playwright
from urllib.parse import urljoin


def scrape_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set headless=False if you want to see the browser
        page = browser.new_page()
        base_url = "https://books.toscrape.com/"
        page.goto(base_url)

        # extract the book component
        books = page.locator("article.product_pod")
        count = books.count()
        print(f"Books found on page {count}")
        
        # check if there are contents found on the page
        if count is None or count <= 0:
            print("No content that was found on the specied page")
            return
        
        # loop of books component and retrive book detail
        for i in range(count):
            book = books.nth(i)
            relative_url = book.locator("h3 > a").get_attribute("href")
            url = urljoin(base_url, relative_url)
            title = book.locator("h3 > a").inner_text()
            price = book.locator("p.price_color").inner_text()
            print(f"Link: {url}, Title: {title}, Price: {price}") 
            
        browser.close()

if __name__ == "__main__":
    scrape_page()
