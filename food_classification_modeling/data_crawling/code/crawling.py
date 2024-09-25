import requests
import json

def crawl_all_foodsafety_data():
    url = 'https://www.foodsafetykorea.go.kr/portal/healthyfoodlife/searchHomeHFProc.do'

    headers = {
        'Cookie': 'mykeyword=; elevisor_for_j2ee_uid=a7q2xjh45ywqc; mykeyword=; _ga=GA1.3.2039212263.1727073061; _ga_Z9ZVQ5VQFN=GS1.3.1727133706.3.0.1727133706.60.0.0; JSESSIONID=yvQFIqGhc8QjkrPnn9OpeuYhpYsjjbOZIrMspR77aeQDfB5CzyT6I7eZzXe7u6zv.amV1c19kb21haW4veGNvd2FzMDFfSVBPMDE=',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'www.foodsafetykorea.go.kr',
        'Origin': 'https://www.foodsafetykorea.go.kr',
        'Referer': 'https://www.foodsafetykorea.go.kr/portal/healthyfoodlife/searchHomeHF.do?menu_grp=MENU_NEW01&amp;menu_no=2823',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # 전체 데이터를 저장할 리스트
    all_data = []

    # 한 번에 가져올 데이터 수
    show_cnt = 500
    start_idx = 1
    total_count = None

    # 데이터가 더 있을 때까지 반복
    while True:
        # POST 요청의 body에 파라미터를 설정
        data = {
            'menu_grp': 'MENU_NEW01',
            'menuNm': '',
            'copyUrl': 'https://www.foodsafetykorea.go.kr:443/portal/healthyfoodlife/searchHomeHF.do?menu_grp=MENU_NEW01&amp;menu_no=2823',
            'search_code': '01',
            'search_word': '',
            'show_cnt': show_cnt,
            'start_idx': start_idx
        }

        # POST 요청 보내기
        response = requests.post(url, headers=headers, data=data)

        # 응답 확인
        if response.status_code == 200:
            # JSON 데이터로 변환
            data = response.json()

            # 첫 요청에서는 total_count를 확인하여 전체 데이터 개수를 확인
            if total_count is None:
                total_count = int(data[0]["total_count"]) if data else 0
                print(f"총 데이터 개수: {total_count}")

            # 응답 데이터를 전체 리스트에 추가
            all_data.extend(data)

            # 현재까지 긁어온 데이터 수
            start_idx += show_cnt

            # 모든 데이터를 가져왔으면 루프 종료
            if start_idx > total_count:
                break

        else:
            print(f"요청 실패. 상태 코드: {response.status_code}")
            break

    print(f"총 {len(all_data)}개의 데이터가 수집되었습니다.")
    return all_data

# 함수 실행
all_food_data = crawl_all_foodsafety_data()

# prdlst_report_ledg_no 값들만 리스트로 추출
prdlst_report_ledg_no_list = [item['prdlst_report_ledg_no'] for item in all_food_data]

# 결과 출력
print(prdlst_report_ledg_no_list)
