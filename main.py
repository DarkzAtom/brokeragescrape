import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import openpyxl
import csv
import json
import requests
from bs4 import BeautifulSoup
import config
import random


california_state = {
    "name": "California",
    "cities": ['Los Angeles', 'San Diego', 'San Jose', 'San Francisco', 'Oakland', 'Sacramento', 'Palm Desert', 'Santa Rosa', 'Long Beach']
    }
washington_state = {
    "name": "Washington",
    "cities": ['Seattle', 'Spokane', 'Tacoma', 'Vancouver', 'Bellevue', 'Kirkland', 'Everett', 'Spokane Valley']
    }
oregon_state = {
    "name": "Oregon",
    "cities": ['Portland', 'Salem', 'Eugene',  'Hillsboro', 'Bend', 'Beaverton', 'Medford', 'Corvallis', 'Springfield', 'Keizer']
    }
colorado_state = {
    "name": "Colorado",
    "cities": ['Denver', 'Colorado Springs', 'Aurora', 'Fort Collins', 'Lakewood', 'Thornton', 'Arvada', 'Westminster', 'Pueblo', 'Boulder']
    }
arizona_state = {
    "name": "Arizona",
    "cities": ['Phoenix', 'Tucson', 'Mesa', 'Chino Valley', 'Gilbert', 'Scottsdale', 'Glendale', 'Peoria', 'Yucca', 'Buckeye']
    }
nevada_state = {
    "name": "Nevada",
    "cities": ['Las Vegas', 'Henderson', 'North Las Vegas', 'Reno', 'Enterprise', 'Spring Valley', 'Sunrise Manor', 'Paradise', 'Sparks', 'Carson City']
    }
texas_state = {
    "name": "Texas",
    "cities": ['Houston', 'San Antonio', 'Dallas', 'Austin', 'Fort Worth', 'El Paso', 'Arlington', 'Corpus Christi', 'Plano', 'Lubbock', 'Laredo', 'McKinney']
    }

us_states_to_scrape = [california_state, washington_state, oregon_state, colorado_state, arizona_state, nevada_state, texas_state]

def rand_proxy():
    proxy = random.choice(config.ip)
    return proxy

def main():
    final_list = []
    page = 0
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("window_size=1280,800")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-save-password-bubble")
    options.add_argument("--lang=en")
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59')
    # proxy = rand_proxy()
    # options.add_argument(f"--proxy-server={proxy}")

    driver = webdriver.Chrome(options=options)

    driver.get("https://www.coldwellbanker.com/sitemap/agents")

    driver.implicitly_wait(10)

    iframe = driver.find_elements(By.TAG_NAME, 'iframe')[0]

    driver.switch_to.frame(iframe)

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, './/*[contains(text(),"Functional and Analytics Cookies")]')))

    no_pref = driver.find_elements(By.XPATH, './/span[contains(text(),"No")]')
    for button in no_pref:
        button.click()

    cookies = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.submit"))).click()

    cookies_close = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, './/*[contains(text(),"Close")]'))).click()
    # washington seatle doesnt have a license number (maybe a washington overall)
    #
    for state in us_states_to_scrape:
        driver.get("https://www.coldwellbanker.com/sitemap/agents")
        driver.implicitly_wait(10)
        state_section = driver.find_element(By.XPATH, f'.//p[contains(text(),"{state["name"]}")]')
        state_section_link = state_section.find_element(By.XPATH, '..').get_attribute('href')
        print(state_section_link)
        time.sleep(3)
        for city in state['cities']:
            driver.get(state_section_link)
            driver.implicitly_wait(10)
            time.sleep(2.7)
            print(city)
            city_section = driver.find_element(By.XPATH, f'.//p[contains(text(),"{city}")]')
            city_section.click()
            driver.implicitly_wait(10)
            time.sleep(2.3)
            while page < 6:
                cards = driver.find_elements(By.CSS_SELECTOR, 'div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-sm-6.css-mgehqq')
                for card in cards:
                    name = card.find_element(By.XPATH, './/h6[@data-testid="office-name"]').text
                    try:
                        licenseNumber = card.find_element(By.XPATH, './/span[@data-testid="license-number"]').text
                    except:
                        licenseNumber = None
                        pass
                    try:
                        phoneNumber = card.find_element(By.XPATH, './/div[@data-testid="phoneNumber"]/a').text
                    except:
                        phoneNumber = None
                        pass
                    try:
                        email = card.find_element(By.XPATH, './/div[@data-testid="emailDiv"]/a').get_attribute('href').split(':')[1]
                    except:
                        email = None
                        pass
                    dictcard = {
                        "name": name,
                        "licenseNumber": licenseNumber,
                        "phoneNumber": phoneNumber,
                        "email": email
                    }
                    print(dictcard)
                    final_list.append(dictcard)
                time.sleep(3.27)
                try:
                    nextpage_button = driver.find_element(By.XPATH, './/button[@aria-label="Go to next page"]')
                    nextpage_button.click()
                    page += 1
                    driver.implicitly_wait(10)
                    time.sleep(3.57)
                except:
                    driver.implicitly_wait(10)
                    time.sleep(3.57)
                    break
            page = 0

    csv_file = "output.csv"

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=final_list[0].keys())
        writer.writeheader()
        for data in final_list:
            writer.writerow(data)



if __name__ == "__main__":
    main()