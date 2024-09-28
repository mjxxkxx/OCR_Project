## dbmongo의 collection 연결
from pymongo import MongoClient
mongoClient = MongoClient("mongodb://localhost:27017")
# database 연결
database = mongoClient["OCR_Progject"]
# collection 작업
collection = database['foodsafetykorea']
# insert 작업 진행
# 크롤링 동작
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

import time


# Chrome 드라이버 설치 디렉터리 설정
# webdriver_manager_directory = ChromeDriverManager().install()

# Chrome 브라우저 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

# WebDriver 생성
browser = webdriver.Chrome()

# DB초기화
collection.delete_many({})

# 웹 페이지 열기  
# 크롤링할 웹 페이지 URL
url = f"https://www.foodsafetykorea.go.kr/portal/healthyfoodlife/searchHomeHF.do?menu_grp=MENU_NEW01&menu_no=2823"
html_source = browser.get(url)

# # 50개씩 보기
# browser.find_element(By.CSS_SELECTOR,value="#show_cnt > option:nth-child(5)").click()
# browser.find_element(By.CSS_SELECTOR,value="#show_cnt").click()
time.sleep(3)

# 페이지네이션 넘기기
while True:
    # 상세보기 들어가기
    item_names = browser.find_elements(By.CSS_SELECTOR,value="tr > td:nth-child(2) > span.table_txt")
    for item_name in item_names:
        item_name.click()
        time.sleep(3)
        items_name = browser.find_element(By.CSS_SELECTOR,value="article > table > tbody > tr:nth-child(2) > td").text
        nutritions = browser.find_element(By.CSS_SELECTOR,value="article > table > tbody > tr:nth-child(13) > td").text
        collection.insert_one({"items_name": items_name, "nutritions": nutritions})
        browser.back()
    browser.find_element(By.CSS_SELECTOR,value="#contents > main > div.list-container > div.board-footer > div > ul > li:nth-child(7) > a").click()
