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

time.sleep(3)
browser.find_element(By.CSS_SELECTOR,value="#contents > main > div.list-container > table > tbody > tr:nth-child(1) > td:nth-child(2)").click()

while True:
    time.sleep(1)
    items_name = browser.find_element(By.CSS_SELECTOR,value="article > table > tbody > tr:nth-child(2) > td").text
    nutritions = browser.find_element(By.CSS_SELECTOR,value="article > table > tbody > tr:nth-child(13) > td").text
    collection.insert_one({"items_name": items_name, "nutritions": nutritions})
    browser.find_element(By.CSS_SELECTOR, value="#contents > main > div.page-container > article > div.board-footer > div.prev-btn-wrap > a:nth-child(2)").click()
