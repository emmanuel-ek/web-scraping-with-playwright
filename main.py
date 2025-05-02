from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import json
from pymongo import MongoClient

data = [] # list of dictionary form the scraped data
client = MongoClient("mongodb://localhost:27017/") # mongo db client

def scrape_page_content(books, limit_per_page, base_url):
    if books is None:
        return
    
    for i in range(limit_per_page):
        book = books.nth(i)
        relative_link = book.locator("h3 > a").get_attribute("href")
        link = urljoin(base_url, relative_link)
        title = book.locator("h3 > a").inner_text()
        price = book.locator("p.price_color").inner_text()
        print(f"Link: {link}, Title: {title}, Price: {price}")
        
        # add scraped data into a list of dictionaries
        data.append({
            'link': link,
            'title': title,
            'price': price
        })

def store_scraped_data_file():
    try:
        with open("books.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print("Data stored on a json file successfully")
    except Exception as e:
        print(f"Error: {str(e)}")

def store_in_mongo_database():
    try:
        db = client['books_db']
        collection = db['playwright_collection']
        collection.insert_many(data)
        print("Data stored in a mongo database successfully")
    except Exception as e:
        print(f"Error: {str(e)}")

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
        first_page_number = int(next_page_info.split()[1]) # first page number 
        
        print(f"Next Page URL: {next_page_url}")
        print(f"Next Page Info: {next_page_info}")
        print(f"Last Page Number: {last_page_number}") 
        print(f"First Page Number: {first_page_number}", end="\n\n")  
        
        # scrape the books details from the first page of the website
        scrape_page_content(books, count, base_url) # this scrapes the first page
        print(end="\n\n")
        
        # Interative deepening scrapper by handling paginated data 
        # by passing the last_page_number as the limit
        # if you want to scrape data untill the last page parameter from the range to 'last_page_number'
        for page_number in range((first_page_number + 1), 10):
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
            print(end='\n\n') # print the new line
            
        browser.close()

if __name__ == "__main__":
    scrape_page()
    store_scraped_data_file() # store the scraped data into a json file
    store_in_mongo_database() # store data in a mongo database
