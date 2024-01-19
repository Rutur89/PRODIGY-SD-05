import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from html.parser import HTMLParser

class BookHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_price = False
        self.in_rating = False
        self.current_data = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'h3' and ('class', 'product-title') in attrs:
            self.in_title = True
        elif tag == 'p' and ('class', 'price_color') in attrs:
            self.in_price = True
        elif tag == 'p' and ('class', 'star-rating') in attrs:
            self.in_rating = True
            self.current_data['Rating'] = attrs[2][1]

    def handle_endtag(self, tag):
        if tag == 'h3':
            self.in_title = False
        elif tag == 'p':
            self.in_price = False
            self.in_rating = False

    def handle_data(self, data):
        if self.in_title:
            self.current_data['Title'] = data
        elif self.in_price:
            self.current_data['Price'] = data

def scrape_books_to_csv():
    # URL of the website to scrape
    base_url = "http://books.toscrape.com/catalogue/category/books_1/index.html"
    base_page = "http://books.toscrape.com/catalogue/category/books_1/page-{0}.html"

    # Initialize a headless Chrome browser with Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
    driver = webdriver.Chrome(options=options)

    # Function to get the total number of pages
    def get_total_pages():
        driver.get(base_url)
        last_page = driver.find_element(By.CLASS_NAME, 'current').text.strip()
        return int(last_page)

    total_pages = get_total_pages()

    # Extract product information
    products = []
    parser = BookHTMLParser()

    for page in range(1, total_pages + 1):
        url = base_page.format(page)
        driver.get(url)

        # Wait for the content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'product_pod'))
        )

        parser.feed(driver.page_source)
        products.extend([parser.current_data.copy()])

    # Save the data to a CSV file
    save_to_csv(products)

    print('Scraping completed. Data saved to "books.csv"')

    # Close the browser
    driver.quit()

def save_to_csv(data):
    # Specify the CSV file name
    csv_file = 'books.csv'

    # Write the data to the CSV file
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['Title', 'Price', 'Rating']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write data
        writer.writerows(data)

if __name__ == '__main__':
    scrape_books_to_csv()
