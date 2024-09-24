import asyncio
import aiohttp
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup

def foodsafety():
    """This function extracts values for each product
    """
    url = 'https://www.foodsafetykorea.go.kr/portal/healthyfoodlife/searchHomeHF.do?menu_grp=MENU_NEW01&amp;menu_no=2823'
    data_dict = {'item_values': []} 

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        tbody = soup.find('tbody')
        if tbody:
            hidden_inputs = tbody.find_all('input', {'type': 'hidden'})

            for input_tag in hidden_inputs:
                value = input_tag.get('value')
                if value:
                    data_dict['item_values'].append(value)  # 리스트에 값 추가
        else:
            print("No tbody found on the page")
    else:
        print("Failed to retrieve the page")

    return data_dict
#############
질문내용
1) ctrl + U = requests
2) 개발자도구 = BeautifulSoup
3) 매크로 = playwright
4) async = 1+2+3 모두 비동기로 작동
이거 맞나요...?
구분이 잘 안가네요...
#############

# 상세 페이지 요청을 위한 함수
async def crawl_details(item_values):
    url = f'https://www.foodsafetykorea.go.kr/portal/healthyfoodlife/searchHomeHFDetail.do?prdlstReportLedgNo={item_values}&amp;search_code=01&amp;start_idx=1&amp;show_cnt=10&amp;menu_no=2823&amp;menu_grp=MENU_NEW01'

    # 비동기 HTTP 세션을 생성하여 여러 요청을 병렬로 실행
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for report_number in report_numbers:
            # 각 신고번호에 대해 비동기적으로 요청을 보내기 위해 task를 추가
            task = asyncio.create_task(fetch_detail_page(session, url, report_number))
            tasks.append(task)

        # 모든 요청 병렬 처리
        responses = await asyncio.gather(*tasks)
        
        # HTML 응답을 처리
        for response in responses:
            soup = BeautifulSoup(response, 'html.parser')
            # 원하는 데이터를 추출할 수 있습니다. 예: 특정 셀렉터에서 텍스트 추출
            table_data = soup.select_one("#contents > main > div.page-container > article > table > tbody > tr:nth-child(13) > td")
            if table_data:
                print("추출된 텍스트:", table_data.get_text())

# 세부 페이지를 요청하는 비동기 함수
async def fetch_detail_page(session, url):
    async with session.get(url) as response:
        print('start crawling from site')
        text = await response.text()
        print('end crawling from site')
        print(text, file = open('add_result.html', 'w+', encoding = 'utf-8'))
        return await response.text()  # HTML을 텍스트로 반환

# main 함수
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 첫 번째 페이지에서 value 가져오기
        await page.goto('https://www.foodsafetykorea.go.kr/portal/healthyfoodlife/searchHomeHF.do?menu_grp=MENU_NEW01&menu_no=2823')
        result = await foodsafety(page)

        # value 기반으로 상세 페이지 크롤링
        await crawl_details(result['item_values'])

        # 브라우저 닫기
        await browser.close()

if __name__ == '__main__':
    print(foodsafety())
    # asyncio.run(main())