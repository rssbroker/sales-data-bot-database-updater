from bs4 import BeautifulSoup
import redis
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import json
import re
import extractor
import list_corrector
import list_updater

r = redis.from_url(os.environ["REDIS_URL"])
email = os.environ["NAMEBIO_EMAIL"]
password = os.environ["NAMEBIO_PASSWORD"]
website_url = "https://namebio.com"
img_path_1 = "table1.png"
img_path_2 = "table2.png"
img_path_3 = "table3.png"

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
    page = get_html_page()
    records_list1 = get_data_from_website(page[0])
    records_list2 = get_data_from_website(page[1])
    records_list3 = get_data_from_website(page[2])
    records_list = records_list1 + records_list2 + records_list3
    prices_b = [x["Price"] for x in records_list]
    prices_a1 = extractor.extract_price_list(img_path_1)
    prices_a2 = extractor.extract_price_list(img_path_2)
    prices_a3 = extractor.extract_price_list(img_path_3)
    prices_a = prices_a1 + prices_a2 + prices_a3
    prices_b = list_corrector.restore_strings(prices_a, prices_b)
    for i in range(len(prices_b)):
        new_dictionary = records_list[i]
        new_dictionary["Price"] = prices_b[i]
        records_list[i] = new_dictionary

    previous_db_data = json.loads(r.get('records_data'))
    new_data = list_updater.find_unique_elements(records_list, previous_db_data)
    r.set('records_data', json.dumps(records_list))

    raw_stack = r.get('stack')
    if raw_stack:
        output_stack = json.loads(r.get('stack'))
        output_stack = output_stack + new_data.reverse()
        r.set('stack', json.dumps(output_stack))
    else:
        output_stack = new_data.reverse()
        r.set('stack', json.dumps(output_stack))


def get_html_page():
    received_html1 = ''
    received_html2 = ''
    received_html3 = ''
    chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    chrome_options = Options()
    options = ["--headless", "--window-size=6000x5000", "--no-sandbox", "--force-device-scale-factor=4.0"]
    
    for option in options:
        chrome_options.add_argument(option)
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    try:
        driver.get(website_url)
        driver.execute_script("document.body.style.zoom = '100%'")
        # Replace WebDriverWait with time.sleep
        time.sleep(10)  # Adjust the sleep duration based on your needs

        # Find the Member Login link
        member_button = driver.find_element(By.LINK_TEXT, 'Member Login')

        # If the login link is present, perform login
        member_button.click()

        # Replace WebDriverWait with time.sleep for subsequent actions
        time.sleep(10)  # Adjust the sleep duration based on your needs

        driver.find_element(By.XPATH, "//*[@id='email']").send_keys(email)
        driver.find_element(
            By.XPATH, "//*[@id='password']").send_keys(password)
        driver.find_element(
            By.CLASS_NAME, "btn-success").click()

        # Replace WebDriverWait with time.sleep for waiting after login
        time.sleep(10)  # Adjust the sleep duration based on your needs

        driver.find_element(By.CLASS_NAME, 'page-logo').click()

        time.sleep(10)

        # Get the URL after login
        button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[2]/a')
        button_next.click()
        time.sleep(10)
        received_html1 = driver.page_source
        table_img = driver.find_element(By.ID, "search-results")
        table_img.screenshot("table1.png")
        
        button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[3]/a')
        button_next.click()
        time.sleep(10)
        received_html2 = driver.page_source
        table_img = driver.find_element(By.ID, "search-results")
        table_img.screenshot("table2.png")
        
        button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[4]/a')
        button_next.click()
        time.sleep(10)
        received_html3 = driver.page_source
        table_img = driver.find_element(By.ID, "search-results")
        table_img.screenshot("table3.png")

    except NoSuchElementException:
        button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[2]/a')
        button_next.click()
        time.sleep(10)
        received_html1 = driver.page_source
        table_img = driver.find_element(By.ID, "search-results")
        table_img.screenshot("table1.png")
        
        button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[3]/a')
        button_next.click()
        time.sleep(10)
        received_html2 = driver.page_source
        table_img = driver.find_element(By.ID, "search-results")
        table_img.screenshot("table2.png")
        
        button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[4]/a')
        button_next.click()
        time.sleep(10)
        received_html3 = driver.page_source
        table_img = driver.find_element(By.ID, "search-results")
        table_img.screenshot("table3.png")

    finally:
        button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[2]/a')
        button_next.click()
        time.sleep(10)
        received_html1 = driver.page_source
        table_img = driver.find_element(By.ID, "search-results")
        table_img.screenshot("table1.png")
        
        button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[3]/a')
        button_next.click()
        time.sleep(10)
        received_html2 = driver.page_source
        table_img = driver.find_element(By.ID, "search-results")
        table_img.screenshot("table2.png")
        
        button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[4]/a')
        button_next.click()
        time.sleep(10)
        received_html3 = driver.page_source
        table_img = driver.find_element(By.ID, "search-results")
        table_img.screenshot("table3.png")
        driver.quit()
        
    return received_html1, received_html2, received_html3


if __name__ == "__main__":
    set_database_records()
