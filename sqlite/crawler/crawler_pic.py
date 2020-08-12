# utf-8

import pandas as pd
import time
import sqlalchemy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlretrieve


ENGINE = sqlalchemy.create_engine('sqlite:///../wfxu.db')


def load_pic(name, title):
    # title = 'Toy Story (1995)'
    option = webdriver.FirefoxOptions()
    option.set_preference('permissions.default.image', 2)
    driver = webdriver.Firefox()
    driver.get('https://www.imdb.com')
    search = driver.find_element_by_id('suggestion-search')
    search.clear()
    search.send_keys(title)
    search.send_keys(Keys.RETURN)
    flag = 0
    for i in range(60):
        if 'class="findSection"' in driver.page_source or 'class="poster"' in driver.page_source:
            flag = 1
            break
        time.sleep(1)
    if not flag:
        driver.close()
        return name, None
    match = driver.find_elements_by_class_name('result_text')
    for i, m in enumerate(match):
        if m.text == title:
            m.find_element_by_tag_name('a').click()
            break
    flag = 0
    for i in range(60):
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
    name, url = '1', 'www'
    with open('item_url.txt', 'a') as f:
        f.write(name + ',' + url + '\n')
    urlretrieve(url, f'..\..\web\static\image\{name}.jpg')


def circle_get():
    data = pd.read_sql("select `movie id`, `movie title` from tb_item", ENGINE)
    pool = ThreadPoolExecutor(8)
    future_list = []
    for i in data.index:
        name = str(data.loc[i, 'movie id'])
        title = data.loc[i, 'movie title']
        future = pool.submit(load_pic, name, title)
        future_list.append(future)
    for f in as_completed(future_list):
        try:
            name, url = f.result()
        except:
            continue
        if not url:
            continue
            print(time.strftime("%Y-%m-%d %X", time.localtime()), name, 'failure!')
        saveData(name, url)
        print(time.strftime("%Y-%m-%d %X", time.localtime()), name)
    pool.shutdown(wait=True)