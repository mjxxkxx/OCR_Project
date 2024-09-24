import asyncio
import aiohttp
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup

async def foodsafety(page):
    # 페이지가 로드되고 특정 테이블 요소가 나타날 때까지 대기
    await page.wait_for_selector("#contents > main > div.list-container > table > tbody > tr > td:nth-child(2)")
    
    # 병렬로 데이터를 가져오기 위해 gather 사용
    item_names_task = page.locator("#contents > main > div.list-container > table > tbody > tr > td:nth-child(2)").all_text_contents()
    company_names_task = page.locator("#contents > main > div.list-container > table > tbody > tr > td:nth-child(3)").all_text_contents()
    report_number_task = page.locator("#contents > main > div.list-container > table > tbody > tr > td:nth-child(4)").all_text_contents()
    
    # 병렬로 비동기 작업 실행
    item_names, company_names, report_number = await asyncio.gather(
        item_names_task, company_names_task, report_number_task
    )
    
    # 슬라이싱
    item_names = [name[3:] for name in item_names]
    company_names = [name[3:] for name in company_names]
    report_number = [number[4:] for number in report_number]
    
    # 딕셔너리로 데이터 저장
    data_dict = {
        "item_names": item_names,
        "company_names": company_names,
        "report_number": report_number
    }

    return data_dict

# 상세 페이지 요청을 위한 함수
async def crawl_details(report_numbers):
    url = 'https://www.foodsafetykorea.go.kr/portal/healthyfoodlife/searchHomeHFDetail.do'

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
    # params = {'prdlstReportLedgNo': '2024021000386672'}  # 신고번호를 파라미터로 전달

    # # async with session.get(url, params=params) as response:
    # headers = {
    #     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    #     "accept-encoding": "gzip, deflate, br, zstd",
    #     "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    #     "cache-control": "max-age=0",
    #     "connection": "keep-alive",
    #     "content-type": "application/x-www-form-urlencoded",
    #     "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    #     "sec-ch-ua-mobile": "?0",
    #     "sec-ch-ua-platform": "Windows",
    #     "sec-fetch-dest": "document",
    #     "sec-fetch-mode": "navigate",
    #     "sec-fetch-site": "same-origin",
    #     "sec-fetch-user": "?1",
    #     "upgrade-insecure-requests": "1",
    #     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    # }

    async with session.get(url) as response:
        print('start crawling from site')
        text = await response.text()
        print('end crawling from site')
        print(text, file = open('add_result.html', 'w+', encoding = 'utf-8'))
        return await response.text()  # HTML을 텍스트로 반환

# main 함수
async def main():
    async with aiohttp.ClientSession() as session:
        await fetch_detail_page(session, 'https://www.foodsafetykorea.go.kr:443/portal/healthyfoodlife/searchHomeHFDetail.do?prdlstReportLedgNo=2024021000386672&amp;search_code=01&amp;start_idx=1&amp;show_cnt=10&amp;menu_no=2823&amp;menu_grp=MENU_NEW01')
    # async with async_playwright() as p:
    #     browser = await p.chromium.launch(headless=False)
    #     page = await browser.new_page()

    #     # 첫 번째 페이지에서 기본 정보 가져오기
    #     await page.goto('https://www.foodsafetykorea.go.kr/portal/healthyfoodlife/searchHomeHF.do?menu_grp=MENU_NEW01&menu_no=2823')
    #     result = await foodsafety(page)

    #     # 신고번호 기반으로 상세 페이지 크롤링
    #     await crawl_details(result['report_number'])

    #     # 브라우저 닫기
    #     await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
    
## 신고번호가 아니라 input의 value값으로 새로 추출 후 다시 크롤링 진행 해야함
