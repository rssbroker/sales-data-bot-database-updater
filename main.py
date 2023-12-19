from bs4 import BeautifulSoup
import redis
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json
import re
import extractor
import list_corrector

r = redis.from_url(os.environ["REDIS_URL"])
email = os.environ["NAMEBIO_EMAIL"]
password = os.environ["NAMEBIO_PASSWORD"]
website_url = "https://namebio.com"
my_dpi = 4.0
img_path = "table.png"


def get_data_from_website(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')


# Find the table with class "table-scrollable"
    table = soup.find('div', class_='table-scrollable')

# Extract data from each row
    data = []
    for row in table.find('tbody').find_all('tr'):
        record = {}
        columns = row.find_all('td')
        # Extracting data from each column

        record['Domain'] = columns[0].find('a').text.strip()
        record['Price'] = columns[1].text.replace(
            '.', '').replace(',', '').replace(' USD', '')
        record['Date'] = columns[2].text.strip()
        record['Venue'] = columns[3].text.strip()

        # Print or store the extracted data as needed
        data.append(record)

    return data


def set_database_records():
    records_list = get_data_from_website(get_html_page())

    prices_b = [x["Price"] for x in records_list]
    prices_a = extractor.extract_price_list(img_path)
    prices_b = list_corrector.restore_strings(prices_a, prices_b)
    for i in range(len(prices_b)):
        new_dictionary = records_list[i]
        new_dictionary["Price"] = prices_b[i]
        records_list[i] = new_dictionary

    r.delete('records_data')
    for record in records_list:
        # Convert the dictionary to a JSON string
        json_data = json.dumps(record)
    # Use RPUSH to push the JSON string to the end of a list
        r.rpush('records_data', json_data)


def get_html_page():
    received_html = ''
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=6000x5000")
    chrome_options.add_argument(f"--force-device-scale-factor={my_dpi}")
    # proxy_server = "47.243.92.199:3128"
    # chrome_options.add_argument(f'--proxy-server={proxy_server}')
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(website_url)
        driver.execute_script("document.body.style.zoom = '100%'")
        # Replace WebDriverWait with time.sleep
        time.sleep(2)  # Adjust the sleep duration based on your needs

        # Find the Member Login link
        member_button = driver.find_element(By.LINK_TEXT, 'Member Login')

        # If the login link is present, perform login
        member_button.click()

        # Replace WebDriverWait with time.sleep for subsequent actions
        time.sleep(2)  # Adjust the sleep duration based on your needs

        driver.find_element(By.XPATH, "//*[@id='email']").send_keys(email)
        driver.find_element(
            By.XPATH, "//*[@id='password']").send_keys(password)
        driver.find_element(
            By.CLASS_NAME, "btn-success").click()

        # Replace WebDriverWait with time.sleep for waiting after login
        time.sleep(2)  # Adjust the sleep duration based on your needs

        driver.find_element(By.CLASS_NAME, 'page-logo').click()

        time.sleep(5)

        # Get the URL after login
        received_html = driver.page_source
        table_img = driver.find_element(By.ID, "search-results")
        table_img.screenshot("table.png")

    except NoSuchElementException:
        received_html = driver.page_source
        time.sleep(5)
        table_img = driver.find_element(By.ID, "search-results")
        table_img.screenshot("table.png")

    finally:
        received_html = driver.page_source
        table_img = driver.find_element(By.ID, "search-results")
        table_img.screenshot("table.png")
        driver.quit()
    return received_html


if __name__ == "__main__":
    set_database_records()
