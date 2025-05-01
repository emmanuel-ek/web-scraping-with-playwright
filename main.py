from playwright.sync_api import sync_playwright
from urllib.parse import urljoin


def scrape_page_content(books, limit, base_url):
    if books is None:
        return
    
    for i in range(limit):
        book = books.nth(i)
        relative_url = book.locator("h3 > a").get_attribute("href")
        url = urljoin(base_url, relative_url)
        title = book.locator("h3 > a").inner_text()
        price = book.locator("p.price_color").inner_text()
        print(f"Link: {url}, Title: {title}, Price: {price}")
        # we will enhance this to store the scraped data into the json and mongo database
    

def scrape_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set headless=False if you want to see the browser
        page = browser.new_page()
        base_url = "https://books.toscrape.com/"
        page.goto(base_url)

        # extract the book component
        books = page.locator("article.product_pod")
        count = books.count()
        print(f"Number of Books Found on First Page: {count}")
            
        # check if there are contents found on the page
        if count is None or count <= 0:
            print("No content that was found on the specied page")
            return

        # next page information
        next_page_url = page.locator("li.next > a").get_attribute("href")
        next_page_info = page.locator("li.current").inner_text().strip()
        last_page_number = int(next_page_info.split()[3]) # The last page is at index 3
        print(f"Next Page URL: {next_page_url}")
        print(f"Next Page Info: {next_page_info}")
        print(f"Last Page Number: {last_page_number}")   
        
        # scrape the books on the first page
        for i in range(count):
            book = books.nth(i)
            # first page details
            relative_url = book.locator("h3 > a").get_attribute("href")
            url = urljoin(base_url, relative_url)
            title = book.locator("h3 > a").inner_text()
            price = book.locator("p.price_color").inner_text()
            #print(f"Link: {url}, Title: {title}, Price: {price}")
        
        # scrape books starting from the first page to the N number of page
        # this will be modified to make it dynamic 
        # by passing the last_page_number as the limit
        for page_number in range(2, 4):
            next_page_relative_url = f"catalogue/page-{page_number}.html"
            next_page_full_url = urljoin(base_url, next_page_relative_url)
            print(f"Next Pages URL: {next_page_full_url}")
            
            # let us crawl to the next pages now
            page.goto(next_page_full_url)
            
            new_books = page.locator("article.product_pod")
            next_page_count = new_books.count()
            print(f"Number of Books Found on Next Pages: {count}")
                
            # check if there are contents found on the page
            if next_page_count is None or next_page_count <= 0:
                print("No content that was found on the specied page")
                break
            
            scrape_page_content(new_books, next_page_count, base_url)
            
            
        browser.close()

if __name__ == "__main__":
    scrape_page()
