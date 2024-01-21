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
from datetime import date

r = redis.from_url(os.environ["REDIS_URL"])
email = os.environ["NAMEBIO_EMAIL"]
password = os.environ["NAMEBIO_PASSWORD"]
website_url = "https://namebio.com"
img_paths = []

def get_data_from_website(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('div', class_='table-scrollable')
    data = []
    for row in table.find('tbody').find_all('tr'):
        record = {}
        columns = row.find_all('td')
        record['Domain'] = columns[0].find('a').text.strip()
        record['Price'] = columns[1].text.replace(
            '.', '').replace(',', '').replace(' USD', '')
        record['Date'] = columns[2].text.strip()
        record['Venue'] = columns[3].text.strip()
        data.append(record)
    return data


def set_total_sales():
    pages = get_html_pages()
    if len(pages) != 0:
        records_list = [get_data_from_website(pages[i]) for i in range(len(pages))]
        records_list = [x for sublist in records_list for x in sublist]
        sales = get_total_sales(str(r.get('date'), encoding='utf-8'), records_list)
        r.set('sales', str(sales))


def get_total_sales(input_date, records_list):
    total_sales = 0
    formatted_input_date = date_parser(input_date)
    for record in records_list:
        record_date = date_parser(record["Date"])
        if date_difference(formatted_input_date, record_date) == 1:
            price = record["Price"]
            price = price.replace(",", "")
            total_sales += int(price)
    return total_sales


def date_difference(date_2: date, date_1: date):
    return (date_2 - date_1).days


def date_parser(input):
    input_split = input.split("-")
    year = int(input_split[0])
    month = int(input_split[1])
    day = int(input_split[2])
    result = date(year, month, day)
    return result


def get_html_pages():
    html_pages = []
    chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    chrome_options = Options()
    options = ["--headless", "--window-size=6000x5000",
               "--no-sandbox", "--force-device-scale-factor=4.0"]
    for option in options:
        chrome_options.add_argument(option)
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    try:
        driver.get(website_url)
        driver.execute_script("document.body.style.zoom = '100%'")
        time.sleep(10)
        member_button = driver.find_element(By.LINK_TEXT, "Member Login")
        member_button.click()
        time.sleep(10)
        driver.find_element(By.XPATH, "//*[@id='email']").send_keys(email)
        driver.find_element(
            By.XPATH, "//*[@id='password']").send_keys(password)
        driver.find_element(
            By.CLASS_NAME, "btn-success").click()
        time.sleep(10)
        driver.find_element(By.CLASS_NAME, 'page-logo').click()
        time.sleep(10)

        button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[2]/a')
        button_next.click()
        time.sleep(10)
        received_html = driver.page_source
        if check_date(received_html):
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[3]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[4]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[5]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[6]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[6]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            while (check_if_end(received_html) == False):
                html_pages.append(received_html)
                button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[6]/a')
                button_next.click()
                time.sleep(10)
                received_html = driver.page_source
            html_pages.append(received_html)

    except NoSuchElementException:
        button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[2]/a')
        button_next.click()
        time.sleep(10)
        received_html = driver.page_source
        if check_date(received_html):
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[3]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[4]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[5]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[6]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[6]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            while (check_if_end(received_html) == False):
                html_pages.append(received_html)
                button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[6]/a')
                button_next.click()
                time.sleep(10)
                received_html = driver.page_source
            html_pages.append(received_html)
    
    finally:
        button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[2]/a')
        button_next.click()
        time.sleep(10)
        received_html = driver.page_source
        if check_date(received_html):
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[3]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[4]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[5]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[6]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            html_pages.append(received_html)
            button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[6]/a')
            button_next.click()
            time.sleep(10)
            received_html = driver.page_source
            while (check_if_end(received_html) == False):
                html_pages.append(received_html)
                button_next = driver.find_element(By.XPATH, '//*[@id="search-results_paginate"]/ul/li[6]/a')
                button_next.click()
                time.sleep(10)
                received_html = driver.page_source
            html_pages.append(received_html)
            driver.quit()
    return html_pages


def check_date(page_source) -> bool:
    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('div', class_='table-scrollable')
    columns = table.find('tbody').find('tr').find_all('td')
    date_column = columns[2].text.strip()
    formatted_date = date_parser(date_column)
    database_date = str(r.get('date'), encoding='utf-8')
    formatted_database_date = date_parser(database_date)
    if formatted_database_date != formatted_date:
        r.set('date', date_column)
        r.set('flag', 'True')
        return True
    else:
        return False
    
def check_if_end(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('div', class_='table-scrollable')
    for row in table.find('tbody').find_all('tr'):
        columns = row.find_all('td')
        date_column = columns[2].text.strip()
        formatted_date = date_parser(date_column)
        database_date = str(r.get('date'), encoding='utf-8')
        formatted_database_date = date_parser(database_date)
        if date_difference(formatted_database_date, formatted_date) == 2:
            return True
    return False


if __name__ == "__main__":
    set_total_sales()
