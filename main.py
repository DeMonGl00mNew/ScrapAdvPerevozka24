from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import requests
import os
from lxml import html
category_dict = {
    'type': (By.XPATH, "//select[@class='common_type_select required']"),
    'category': (By.XPATH, "//select[@class='cat_id_select required']"),
    'country': (By.XPATH, "//select[@class='country_select required']"),
    'region': (By.XPATH, "//select[@class='region_select required']"),
    'city': (By.XPATH, "//select[@class='city_select']")
}

SHOW_FINDS_BUTTON = (By.XPATH, "//button[@class='master-button v-extra v-middle show-items']")
FINDS_COMPANIES = (By.XPATH, "//div[@class='c-company-card']")

OPTION_IS_STALENESS=(By.XPATH, "//div[@class='c-company-card']")

def main():
    url = 'https://perevozka24.ru/search-items?cat_id=0&region_id=0&city_id='
    driver = webdriver.Chrome()
    driver.get(url)
    for index, (key, value) in enumerate(category_dict.items()):
        SelectingCategory(value, driver,index)

    driver.find_element(*SHOW_FINDS_BUTTON).click()
    time.sleep(1)

    url=driver.current_url#'https://perevozka24.ru/moskva-50/arenda-passazhirskogo-transporta-mikroavtobusy'#
    parsingByLxml(url, 'index.htm')
    time.sleep(100)


debuging_input = [4, 2, 2, 1, 2]



def parsing_info(driver:webdriver):
    current_url = driver.current_url
    print("Адрес текущей веб-страницы:", current_url)

def SelectingCategory(locator, driver,index):


    element = driver.find_element(*locator)
    try:
        next_locator=category_dict[list(category_dict.keys())[index+1]]
    except:
        next_locator=locator
    next_element= driver.find_element(*next_locator).find_element(*(By.XPATH, ".//option[2]"))

    DROPDOWN = Select(element)
    all_options = DROPDOWN.options
    for i, option in enumerate(all_options):
       # print(f"{i + 1} {option.text}")
        pass

    category_index = debuging_input[index]  # int(input(f"Выберите номер категории: "))
    #print("-" * 20)
    try:
        DROPDOWN.select_by_index(category_index - 1)
    except:
        wait = WebDriverWait(driver, 30, poll_frequency=1)
        wait.until(EC.staleness_of(next_element))
        DROPDOWN.select_by_index(category_index - 1)

def parsingByLxml(url, name_file):
    src=getHTML_text(url,name_file)
    tree = html.fromstring(src)
    ROOT_ADV="(//*[contains(@class,'c-ad-item updi')])"
    FIRST_NAMES="//*[@target='_blank']/text()"
    SECOND_NAMES="//*[@class='cb-name']//*[@class='javalnk blank']//text()"
    PHONES="//*[contains(@rel,'tel')]/text()"
    PRICE="//*[contains(@class,'pagi')]/following-sibling::*[@class='ai-price']//*[@class='ai-item']//*[@class='ai-value']"
    root_adv=tree.xpath(ROOT_ADV)
    for adv in root_adv[:-1]:
        print(''.join(adv.xpath("."+FIRST_NAMES)).strip())
        print(''.join(adv.xpath("."+SECOND_NAMES)).strip())
        print(" ".join([i.strip() for i in adv.xpath("."+PHONES)]).strip())
        price_join=list(zip( adv.xpath("."+PRICE+"//text()"),adv.xpath("."+PRICE+"/following-sibling::*[@class='ai-label']//text()")))
        price_join=''.join([''.join(i) for i in price_join])
        price_join =price_join.replace("\n", "")
        price_join= " ".join(price_join.split())
        print(price_join)
        print('-'*20)




def getHTML_text(url, name_file='',force_write=False):

    if not os.path.exists(name_file) or force_write==True:
        req = requests.get(url)
        src=req.text
        with open(name_file, "w",encoding="utf-8") as file:
            file.write(src)
        return src
    else  :
        with open(name_file,"r",encoding="utf-8") as file:
            return file.read()




if __name__ == '__main__':
    main()
