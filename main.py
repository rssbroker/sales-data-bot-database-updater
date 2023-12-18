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

r = redis.from_url(os.environ["REDIS_URL"])
email = os.environ["NAMEBIO_EMAIL"]
password = os.environ["NAMEBIO_PASSWORD"]
website_url = "https://namebio.com"
my_dpi = 4.0


def get_data_from_website(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')


# Find the table with class "table-scrollable"
    table = soup.find('div', class_='table-scrollable').find('table')

# Extract data from each row
    data = []
    for row in table.find('tbody').find_all('tr'):
        domain = row.find('a', class_='domain-details-link').get('href')
        price = re.search(
            r'(\d[\d,.]*) USD', row.find_all('td')[1].text).group(1).replace(',', '')
        date = row.find_all('td')[2].text
        venue = row.find_all('td')[3].text

        data.append({
            'Domain': domain,
            'Price': price,
            'Date': date,
            'Venue': venue
        })

    return data


def set_database_records():
    records_list = get_data_from_website(get_html_page())
    r.delete('records_data')
    for record in records_list:
        # Convert the dictionary to a JSON string
        json_data = json.dumps(record)
    # Use RPUSH to push the JSON string to the end of a list
        r.rpush('records_data', json_data)


def get_html_page():
    received_html = ''
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
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
        member_button = driver.find_element(By.LINK_TEXT, "Member Login")

        # If the login link is present, perform login
        member_button.click()

        # Replace WebDriverWait with time.sleep for subsequent actions
        time.sleep(2)  # Adjust the sleep duration based on your needs

        driver.find_element(By.XPATH, "//*[@id='email']").send_keys(email)
        driver.find_element(
            By.XPATH, "//*[@id='password']").send_keys(password)
        driver.find_element(
            By.XPATH, "/html/body/div[7]/div[2]/div/div[3]/button").click()

        # Replace WebDriverWait with time.sleep for waiting after login
        time.sleep(2)  # Adjust the sleep duration based on your needs

        # Get the URL after login
        received_html = driver.page_source
        table_img = driver.find_element(By.ID, "search-results")
        table_img.screenshot("table.png")

    except NoSuchElementException:
        received_html = driver.page_source
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
