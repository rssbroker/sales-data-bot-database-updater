from bs4 import BeautifulSoup
import redis
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

r = redis.from_url(os.environ["REDIS_URL"])
email = os.environ["NAMEBIO_EMAIL"]
password = os.environ["NAMEBIO_PASSWORD"]
website_url = "https://namebio.com"

def get_data_from_website(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find the table with the specified ID
    table = soup.find('table-scrollable', {'id': 'search-results'})
    records = []
    # Check if the table is found
    if table:
        # Find all rows in the table body

        rows = table.find('tbody').find_all('tr')

        # Iterate through rows and extract data
        for row in rows:
            record = {}
            columns = row.find_all('td')
            # Extracting data from each column

            record['domain'] = columns[0].find('a').get('href')
            record['price'] = columns[1].text.replace(' USD', '')
            record['date'] = columns[2].text
            record['venue'] = columns[3].text

            # Print or store the extracted data as needed
            records.append(record)

    return records

def set_database_records():
  records_list = get_data_from_website(get_html_page())
    r.delete('records_data')
    for record in records_list:
        # Convert the dictionary to a JSON string
        json_data = json.dumps(record)
    # Use RPUSH to push the JSON string to the end of a list
        r.rpush('records_data', json_data)

def get_html_page()
  received_html = ''
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    #proxy_server = "47.243.92.199:3128"
    #chrome_options.add_argument(f'--proxy-server={proxy_server}')
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(website_url)

        # Replace WebDriverWait with time.sleep
        time.sleep(2)  # Adjust the sleep duration based on your needs

        # Find the Member Login link
        member_button = driver.find_element(By.LINK_TEXT, "Member Login")

        # If the login link is present, perform login
        member_button.click()

        # Replace WebDriverWait with time.sleep for subsequent actions
        time.sleep(2)  # Adjust the sleep duration based on your needs

        driver.find_element(By.XPATH, "//*[@id='email']").send_keys(email)
        driver.find_element(By.XPATH, "//*[@id='password']").send_keys(password)
        driver.find_element(By.XPATH, "/html/body/div[7]/div[2]/div/div[3]/button").click()

        # Replace WebDriverWait with time.sleep for waiting after login
        time.sleep(2)  # Adjust the sleep duration based on your needs

        # Get the URL after login
        received_html = driver.page_source

    except NoSuchElementException:
        received_html = driver.page_source

    finally:
        driver.quit()
    return received_html

if __name__ == "__main__":
    set_database_records()
