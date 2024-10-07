import cv2
import numpy as np
from PIL import Image
import requests
import base64
import uuid
import time
import os
import matplotlib.pyplot as plt
import re

# API 설정
api_url = ''
secret_key = ''
image_folder = r''


# 영양 성분 키워드
nutrition_keywords = {
    '칼로리': r'(\d+\.?\d*)\s*kcal',
    '탄수화물': r'탄수화물\s*:?(\d+\.?\d*\s*g)',
    '단백질': r'단백질\s*:?(\d+\.?\d*\s*g)',
    '지방': r'지방\s*:?(\d+\.?\d*\s*g)',
    '당류': r'당류\s*:?(\d+\.?\d*\s*g)',
    '포화지방': r'포화지방\s*:?(\d+\.?\d*\s*g)',
    '트랜스지방': r'트랜스지방\s*:?(\d+\.?\d*\s*g)',
    '나트륨': r'나트륨\s*:?(\d+\.?\d*\s*mg)', 
    '콜레스테롤': r'콜레스테롤\s*:?(\d+\.?\d*\s*mg)',
    '식이섬유': r'식이섬유\s*:?(\d+\.?\d*\s*g)',
    '칼슘': r'칼슘\s*:?(\d+\.?\d*\s*mg)',
    '철': r'철\s*:?(\d+\.?\d*\s*mg)',
}

# CLAHE를 사용한 대비 향상 함수
def enhance_contrast(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)

# 다양한 전처리 방법 적용
def preprocess_images(image):
    # 원본 그레이스케일 변환
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    processed_images = []

    # 1. 기본 그레이스케일
    processed_images.append(gray)

    # 2. CLAHE 적용 (대비 향상)
    clahe_image = enhance_contrast(image)
    processed_images.append(clahe_image)

    return processed_images

# OCR 요청을 위한 이미지 인코딩 함수
def encode_image_for_ocr(image):
    _, img_encoded = cv2.imencode('.jpg', image)
    return base64.b64encode(img_encoded).decode('utf-8')

# 텍스트에서 영양 성분 추출 함수
def extract_nutrition_info(text):
    extracted_info = []
    for nutrient, pattern in nutrition_keywords.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # 칼로리일 경우 단위 추가
            if nutrient == '칼로리':
                extracted_info.append((nutrient, match.group(1) + ' kcal'))
            else:
                extracted_info.append((nutrient, match.group(1)))
    return extracted_info

# 이미지 처리 및 OCR 요청 루프
for filename in os.listdir(image_folder):
    if filename.lower().endswith('.jpg'):
        image_file = os.path.join(image_folder, filename)
        print(f"Processing file: {os.path.abspath(image_file)}")

        # 이미지 로드
        try:
            image = Image.open(image_file)
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"이미지를 로드할 수 없습니다: {image_file}, 오류: {e}")
            continue

        # 다양한 전처리 이미지 생성
        processed_images = preprocess_images(image)
        all_texts = []

        # 각 전처리 이미지에 대해 OCR 요청 실행
        for idx, processed_image in enumerate(processed_images):
            headers = {
                'X-OCR-SECRET': secret_key,
                'Content-Type': 'application/json'
            }

            image_content = encode_image_for_ocr(processed_image)

            request_json = {
                'images': [
                    {
                        'format': 'jpg',
                        'name': f"{filename}_variant_{idx}",
                        'data': image_content
                    }
                ],
                'requestId': str(uuid.uuid4()),
                'version': 'V2',
                'timestamp': int(round(time.time() * 1000))
            }

            try:
                response = requests.post(api_url, headers=headers, json=request_json, timeout=60)
                if response.status_code == 200:
                    ocr_results = response.json()
                    for image_result in ocr_results['images']:
                        for field in image_result['fields']:
                            text = field['inferText']
                            all_texts.append(text)
                else:
                    print(f"OCR 결과를 받아오지 못했습니다. 상태 코드: {response.status_code} for {filename}")

            except requests.exceptions.RequestException as e:
                print(f"요청 중 오류 발생: {e} for {filename}")

        # 전체 텍스트를 하나로 합침
        full_text = ' '.join(all_texts)

        # 영양 성분 정보 추출 및 출력
        nutrition_info = extract_nutrition_info(full_text)
        if nutrition_info:
            print(f"Extracted Nutrient Information for {filename}:")
            for nutrient, value in nutrition_info:
                print(f"{nutrient}: {value}")
        else:
            print(f"No relevant nutrition info found for {filename}")

        # 원본 이미지와 전처리된 이미지 출력
        fig, axs = plt.subplots(1, len(processed_images) + 1, figsize=(10,5))
        axs[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        axs[0].set_title('Original Image')
        axs[0].axis('off')

        for i, processed_image in enumerate(processed_images):
            axs[i + 1].imshow(processed_image, cmap='gray')
            axs[i + 1].set_title(f'Processed Image {i+1}')
            axs[i + 1].axis('off')

        plt.show()
