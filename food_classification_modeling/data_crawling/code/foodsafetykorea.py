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
async def fetch_detail_page(session, url, report_number):
    params = {'prdlstReportLedgNo': report_number}  # 신고번호를 파라미터로 전달
    async with session.get(url, params=params) as response:
        return await response.text()  # HTML을 텍스트로 반환

# main 함수
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 첫 번째 페이지에서 기본 정보 가져오기
        await page.goto('https://www.foodsafetykorea.go.kr/portal/healthyfoodlife/searchHomeHF.do?menu_grp=MENU_NEW01&menu_no=2823')
        result = await foodsafety(page)

        # 신고번호 기반으로 상세 페이지 크롤링
        await crawl_details(result['report_number'])

        # 브라우저 닫기
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
