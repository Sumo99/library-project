from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
import traceback
import time
options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")

driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)
driver.get('https://carverlib.ent.sirsi.net/client/en_US/default/search/results?qf=ITYPE%09Material+Type%091%3AADULT-BOOK%09Adult+Book&rw=12&av=0&isd=true')
for i in range(0,12):
        print("Clicking on element "+ str(i))
        driver.find_element_by_xpath(f'//*[@id="detailLink{i + 12}"]').click()
        print("Located element")
        print("The title is "+WebDriverWait(driver,30).until(EC.visibility_of_element_located((By.XPATH, f'//*[@id="detail_biblio{i + 12}"]/div[1]/div/div/div[2]'))).text)
        try:
            print("The isbn is "+WebDriverWait(driver,30).until(EC.visibility_of_element_located((By.XPATH, f"//*[@id='detail_biblio{i + 12}']/div[contains(. , 'ISBN')]"))).text[6:])
        except:
            print("The page has no isbn!")
        # print("The link is " + "https://carverlib.ent.sirsi.net/client/en_US/default/search/detailnonmodal/ent:$002f$002fSD_ILS$002f0$002fSD_ILS:34902/one?qu=9781593577841&dt=list")
       
        try:
            print("The number of pages is " + driver.find_element_by_xpath(f"//*[@id='detail_biblio{i + 12}']/div[contains(. , 'Physical Description')]").text)
        except:
            print("There are an unknown number of pages")
       
        print(driver.find_element_by_xpath (f'//*[@id="detailCover{i + 12}"]').get_attribute("src"))
 
        time.sleep(5)
        summaryList = driver.find_elements_by_css_selector('a[href="#tabs-4"]')
        elementToClick = summaryList[len(summaryList) - 1]
        driver.execute_script("arguments[0].click();", elementToClick)
        Desc = ""
        paragraphText = driver.find_elements_by_css_selector("div.enrichedContentElement")
        paragraph = paragraphText[len(paragraphText) - 1].find_elements_by_tag_name("p")
        for element in paragraph:
            Desc = element.text + Desc
        print(Desc)
        WebDriverWait(driver,30).until(lambda x: x.execute_script("""return document.querySelectorAll('[title="Close"]')[0]"""))
        driver.execute_script("""document.querySelectorAll('[title="Close"]')[document.querySelectorAll('[title="Close"]').length - 1].click();""")
        WebDriverWait(driver,30).until(lambda x: x.execute_script("""return document.querySelectorAll('[title="Close"]')[0]"""))
        driver.execute_script("""document.querySelectorAll('[title="Close"]')[document.querySelectorAll('[title="Close"]').length - 1].click();""")
