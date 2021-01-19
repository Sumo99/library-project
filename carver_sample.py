from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)
driver.get('https://carverlib.ent.sirsi.net/client/en_US/default/search/results?qf=ITYPE%09Material+Type%091%3AADULT-BOOK%09Adult+Book&av=0&isd=true')
for i in range(0,12):
    try:
        print("Clicking on element "+ str(i))
        driver.find_element_by_xpath(f'//*[@id="detailLink{i}"]').click()
        print("Located element")
        print("The title is "+WebDriverWait(driver,30).until(EC.visibility_of_element_located((By.XPATH, f'//*[@id="detail_biblio{i}"]/div[1]/div/div/div[2]'))).text)
        print("The isbn is "+WebDriverWait(driver,30).until(EC.visibility_of_element_located((By.XPATH, f'//*[@id="detail_biblio{i}"]/div[3]/div/div/div[2]'))).text)
        WebDriverWait(driver,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a[href="#tabs-4"]'))).click() # for the first element
        print("The description is "+WebDriverWait(driver,30).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="tabs-4"]/div[1]/p'))).text)
        driver.execute_script("""document.querySelectorAll('[title="Close"]')[document.querySelectorAll('[title="Close"]').length - 1].click();""")
        print("Closed element")
    except:
       summaryList = driver.find_elements_by_css_selector('a[href="#tabs-4"]')
       summaryList[len(summaryList) - 1].click()
       Desc = ""
       paragraphText = driver.find_elements_by_css_selector("div.enrichedContentElement")[i].find_elements_by_tag_name("p")
       for element in paragraphText:
           Desc = element.text + Desc
       print(Desc)
       WebDriverWait(driver,30).until(lambda x: x.execute_script("""return document.querySelectorAll('[title="Close"]')[0]"""))
      driver.execute_script("""document.querySelectorAll('[title="Close"]')[document.querySelectorAll('[title="Close"]').length - 1].click();""")

