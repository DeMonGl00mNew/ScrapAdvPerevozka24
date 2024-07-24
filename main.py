import os
import requests
import os, glob
import json
import csv
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Словарь с локаторами для категорий
category_dict = {
    'type': (By.XPATH, "//select[@class='common_type_select required']"),
    'category': (By.XPATH, "//select[@class='cat_id_select required']"),
    'country': (By.XPATH, "//select[@class='country_select required']"),
    'region': (By.XPATH, "//select[@class='region_select required']"),
    'city': (By.XPATH, "//select[contains(@class,'city_select')]")
}

# Локаторы кнопок и элементов на странице
SHOW_FINDS_BUTTON = (By.XPATH, "//button[@class='master-button v-extra v-middle show-items']")
FINDS_COMPANIES = (By.XPATH, "//div[@class='c-company-card']")
OPTION_IS_STALENESS = (By.XPATH, "//div[@class='c-company-card']")
previous_adv = ""

# Основная функция
def main():
    rewrite_files = RewriteHtmlFolderFiles()

    url = 'https://perevozka24.ru/search-items?cat_id=0&region_id=0&city_id='
    driver = webdriver.Chrome()
    driver.get(url)
    for index, (key, value) in enumerate(category_dict.items()):
        SelectingCategory(value, driver, index)

    driver.find_element(*SHOW_FINDS_BUTTON).click()
    number_page = ""

    while True:
        url = driver.current_url + f"/{number_page}"
        if not ParsingByLxml(url, f'index{number_page}.htm', rewrite_files):
            break
        number_page = 2 if number_page == "" else number_page + 1

    JsonWriteFile(list_of_adv_info)
    CsvWriteFile(list_of_adv_info)

# Функция для записи данных в JSON файл
def JsonWriteFile(list_for_json: list):
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(list_for_json, file, indent=4, ensure_ascii=False)

# Функция для записи данных в CSV файл
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

# Функция выбора категории
def SelectingCategory(locator: tuple, driver, index):
    try:
        next_locator = category_dict[list(category_dict.keys())[index + 1]]
    except:
        return

    wait = WebDriverWait(driver, 10, poll_frequency=1)

    element = wait.until(EC.visibility_of_element_located(locator))

    next_element_option = wait.until(EC.visibility_of_element_located((By.XPATH, next_locator[1] + "//option")))

    DROPDOWN = Select(element)
    all_options = DROPDOWN.options

    for i, option in enumerate(all_options):
        print(f"{i + 1} {option.text}")

    category_index = int(input(f"Выберите номер категории: "))
    print("-" * 20)
    DROPDOWN.select_by_index(category_index - 1)
    try:
        if (index == 0 or index == 2 or index == 3):
            wait = WebDriverWait(driver, 10, poll_frequency=1)
            wait.until(EC.staleness_of(next_element_option))
    except:
        pass

# Функция удаления пробельных символов
def DelWhitespaceCharacters(listForJoin: list) -> str:
    string_result = ""
    for corteg in listForJoin:
        for string in corteg:
            string_result += string.strip() + " "
    return string_result

# Функция перезаписи файлов в директории
def RewriteHtmlFolderFiles():
    while True:
        rewrite_files = input("Переписать html файлы в директории если выбрана другая категория 1-да / иначе 0-нет: ")
        if rewrite_files == '0' or rewrite_files == '1':
            rewrite_files = bool(int(rewrite_files))
            break
    if rewrite_files:
        for f in glob.glob("index*.htm"):
            os.remove(f)
    return rewrite_files

list_of_adv_info = []

# Функция парсинга с помощью lxml
def ParsingByLxml(url, name_file, rewrite_files) -> bool:
    global previous_adv

    src = GetHtmlText(url, name_file, rewrite_files)
    tree = html.fromstring(src)
    ROOT_ADV = "(.//*[contains(@class,'c-ad-item updi')])"
    FIRST_NAMES = "//*[@target='_blank']/text()"
    SECOND_NAMES = "//*[@class='cb-name']//*[@class='javalnk blank']//text()"
    RATING = "//*[@class='place-in-rating']//text()"
    PHONES = "//*[contains(@rel,'tel')]/text()"
    PRICE = "//*[contains(@class,'pagi')]/following-sibling::*[@class='ai-price']//*[@class='ai-item']//*[@class='ai-value']"
    ID_INDEX = "//*[contains(@onclick,'clickPhone')]/@onclick"
    root_adv = tree.xpath(ROOT_ADV)

    if not root_adv:
        return False

    if previous_adv != "" and previous_adv == root_adv[-1].xpath("." + ID_INDEX)[-1]:
        return False

    previous_adv = root_adv[-1].xpath("." + ID_INDEX)[-1]

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

# Функция получения HTML текста
def GetHtmlText(url, name_file='', force_write=True):
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
