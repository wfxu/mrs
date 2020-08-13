# utf-8

import pandas as pd
import time
import os
import sqlalchemy
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlretrieve


ENGINE = sqlalchemy.create_engine('sqlite:///../wfxu.db')


def load_pic(name, title):
    # title = 'Toy Story (1995)'
    option = webdriver.FirefoxOptions()
    option.set_preference('permissions.default.image', 2)
    driver = webdriver.Firefox(firefox_options=option)
    driver.maximize_window()
    try:
        driver.get('https://www.imdb.com')
        search = driver.find_element_by_id('suggestion-search')
    except exceptions.WebDriverException:
        return name, None        
    search.clear()
    search.send_keys(title)
    search.send_keys(Keys.RETURN)
    flag = 0
    time.sleep(3)
    try:
        driver.page_source
    except exceptions.WebDriverException:
        return name, None
    for i in range(15):
        if 'class="findSection"' in driver.page_source or 'class="poster"' in driver.page_source:
            flag = 1
            break
        time.sleep(1)
    if not flag:
        driver.close()
        return name, None
    match = driver.find_elements_by_class_name('result_text')
    flag = 0
    for m in match:
        if m.text == title:
            try:
                m.find_element_by_tag_name('a').click()
            except:
                driver.close()
                return name, None
            flag = 1
            break
    if not flag:
        driver.close()
        return name, None
    flag = 0
    time.sleep(3)
    try:
        driver.page_source
    except exceptions.WebDriverException:
        return name, None
    for i in range(15):
        if 'class="poster"' in driver.page_source:
            flag = 1
            break
        time.sleep(1)
    if not flag:
        driver.close()
        return name, None
    xpath = "//div[@class='poster']/a/img"
    img = driver.find_element_by_xpath(xpath)
    url = img.get_attribute('src')
    driver.close()
    return name, url
        


def saveData(name, url):
    with open('item_url.txt', 'a') as f:
        f.write(name + ',' + url + '\n')
    urlretrieve(url, f'..\..\web\static\image\{name}.jpg')


def circle_get():
    data = pd.read_sql("select `movie_id`, `movie_title` from tb_item", ENGINE)
    file_dir = '..\image'
    file_exists = [os.path.splitext(f)[0] for f in os.listdir(file_dir) if os.path.splitext(f)[1] == '.jpg']
    pool = ThreadPoolExecutor(4)
    future_list = []
    for i in data.index:
        name = str(data.loc[i, 'movie id'])
        if name in file_exists:
            continue
        title = data.loc[i, 'movie title']
        future = pool.submit(load_pic, name, title)
        future_list.append(future)
    for f in as_completed(future_list):
        name, url = f.result()
        if not url:
            print(time.strftime("%Y-%m-%d %X", time.localtime()), name, 'failure!')
            continue
        saveData(name, url)
        print(time.strftime("%Y-%m-%d %X", time.localtime()), name)
    pool.shutdown(wait=True)


if __name__ == '__main__':
    circle_get()