import time
import requests
import os
import json
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import html
from pprint import pprint

category_dict = {
    'type': (By.XPATH, "//select[@class='common_type_select required']"),
    'category': (By.XPATH, "//select[@class='cat_id_select required']"),
    'country': (By.XPATH, "//select[@class='country_select required']"),
    'region': (By.XPATH, "//select[@class='region_select required']"),
    'city': (By.XPATH, "//select[@class='city_select']")
}
SHOW_FINDS_BUTTON = (By.XPATH, "//button[@class='master-button v-extra v-middle show-items']")
FINDS_COMPANIES = (By.XPATH, "//div[@class='c-company-card']")
OPTION_IS_STALENESS = (By.XPATH, "//div[@class='c-company-card']")

debuging_input = [2, 5, 2, 1, 2]


def main():
    url = 'https://perevozka24.ru/search-items?cat_id=0&region_id=0&city_id='
    driver = webdriver.Chrome()
    driver.get(url)
    for index, (key, value) in enumerate(category_dict.items()):
        SelectingCategory(value, driver, index)

    driver.find_element(*SHOW_FINDS_BUTTON).click()
    time.sleep(1)
    number_page = ""
    while True:
        url = driver.current_url + f"/{number_page}"  # 'https://perevozka24.ru/moskva-50/arenda-passazhirskogo-transporta-mikroavtobusy'#

        if not ParsingByLxml(url, f'index{number_page}.htm'):
            break
        number_page = 2 if number_page == "" else number_page + 1
    JsonWriteFile(list_of_adv_info)
    CsvWriteFile(list_of_adv_info)
    time.sleep(100)


def JsonWriteFile(list_for_json: list):
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(list_for_json, file, indent=4, ensure_ascii=False)


def CsvWriteFile(list_for_csv: list):
    with open('data.csv', 'w', newline='') as file:
        header_list = ['fist_name',
                       'second_name',
                       'rating',
                       'phone',
                       'price']
        writer = csv.DictWriter(file, fieldnames=header_list)
        writer.writeheader()
        for adv_dict in list_for_csv:
            writer.writerow(adv_dict)

def ParsingInfo(driver: webdriver):
    current_url = driver.current_url
    print("Адрес текущей веб-страницы:", current_url)


def SelectingCategory(locator, driver, index):
    element = driver.find_element(*locator)
    try:
        next_locator = category_dict[list(category_dict.keys())[index + 1]]
    except:
        next_locator = locator
    next_element = driver.find_element(*next_locator).find_element(*(By.XPATH, ".//option[2]"))

    DROPDOWN = Select(element)
    try:
        all_options = DROPDOWN.options
    except:
        wait = WebDriverWait(driver, 30, poll_frequency=1)
        wait.until(EC.presence_of_all_elements_located(next_element))
        all_options = DROPDOWN.options
    for i, option in enumerate(all_options):
        print(f"{i + 1} {option.text}")

    category_index = int(input(f"Выберите номер категории: "))#debuging_input[index]
    print("-" * 20)
    try:
        DROPDOWN.select_by_index(category_index - 1)
    except:
        wait = WebDriverWait(driver, 30, poll_frequency=1)
        wait.until(EC.staleness_of(next_element))
        DROPDOWN.select_by_index(category_index - 1)


def DelWhitespaceCharacters(listForJoin: list) -> str:
    string_result = ""
    for corteg in listForJoin:
        for string in corteg:
            string_result += string.strip() + " "
    return string_result


list_of_adv_info = []


def ParsingByLxml(url, name_file) -> bool:
    src = GetHtmlText(url, name_file)
    tree = html.fromstring(src)
    ROOT_ADV = "(.//*[contains(@class,'c-ad-item updi')])"
    FIRST_NAMES = "//*[@target='_blank']/text()"
    SECOND_NAMES = "//*[@class='cb-name']//*[@class='javalnk blank']//text()"
    RATING = "//*[@class='place-in-rating']//text()"
    PHONES = "//*[contains(@rel,'tel')]/text()"
    PRICE = "//*[contains(@class,'pagi')]/following-sibling::*[@class='ai-price']//*[@class='ai-item']//*[@class='ai-value']"
    root_adv = tree.xpath(ROOT_ADV)

    if not root_adv:
        return False

    for i, adv in enumerate(root_adv):
        dictAdv = {}.fromkeys(["fist_name", "second_name", "rating", "phone", "price"])
        dictAdv["fist_name"] = ' '.join([i.strip() for i in adv.xpath("." + FIRST_NAMES)])
        dictAdv["second_name"] = ' '.join([i.strip() for i in adv.xpath("." + SECOND_NAMES)])
        dictAdv["rating"] = ' '.join([i.strip() for i in adv.xpath("." + RATING)])
        dictAdv["phone"] = ' '.join([i.strip() for i in adv.xpath("." + PHONES)]).strip()

        price_join = list(zip(adv.xpath("." + PRICE + "//text()"),
                              adv.xpath("." + PRICE + "/following-sibling::*[@class='ai-label']//text()")))
        dictAdv["price"] = DelWhitespaceCharacters(price_join)
        list_of_adv_info.append(dictAdv)
    return True



def GetHtmlText(url, name_file='', force_write=False):
    if not os.path.exists(name_file) or force_write == True:
        req = requests.get(url)
        src = req.text
        with open(name_file, "w", encoding="utf-8") as file:
            file.write(src)
        return src
    else:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()


if __name__ == '__main__':
    main()
