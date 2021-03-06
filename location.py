from selenium import * 
from selenium.webdriver.chrome.options import Options  
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

def get_location(url):
    options = Options()     
    options.add_argument("--headless")    
    options.binary_location = "/usr/bin/chromium" 
    driver = webdriver.Chrome(chrome_options=options, executable_path="/home/sumo/webDriver/chromedriver")  
    driver.get(url) 
    locations = []

    try:
        w = WebDriverWait(driver, 10)
        w.until(EC.presence_of_element_located((By.XPATH ,"//*[@id='holdsRequestBlock']/button")))
        print("Page load happened")
    except TimeoutException:
        print("Timeout happened no page load")

    button = driver.find_element_by_xpath('//*[@id="holdsRequestBlock"]/button')
    button.click()


    try:
        w = WebDriverWait(driver, 10)
        w.until(EC.presence_of_element_located((By.CLASS_NAME ,"responsive_details_table")))
        print("Page load happened")
    except TimeoutException:
        print("Timeout happened no page load")

    divs = driver.find_elements_by_class_name("responsive_details_table")[0]

    table_elements = divs.find_elements_by_css_selector("[data-label='Location']")

    for element in table_elements:
        locations.append(element.text)

    return  locations

if __name__ == "__main__":
    print(get_location("https://hclib.bibliocommons.com/item/show/5867816109"))
