import time
import pandas as pd
import cv2
import json
import matplotlib.pyplot as plt
import requests
import uuid
import os
import numpy as np
from PIL import Image
import base64

# Set display options for pandas
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 5000)

# API Gateway Invoke URL and Secret Key
api_url = 'https://ql83sffmog.apigw.ntruss.com/custom/v1/34535/06797cb00558c159cb06e810ab3a4f931278516b50f25ac4b2858bed67990773/general'
secret_key = 'ZWZmVVVnS0FaS0xUREFacWVXQmN3bEdwV3l4Um9sZks='
image_folder = r'C:\Users\user\Documents\GitHub\OCR_Project\study_file\mj\캔'

# Loop through all JPG files in the specified directory
for filename in os.listdir(image_folder):
    if filename.lower().endswith('.jpg'):
        image_file = os.path.join(image_folder, filename)

        print(f"Processing file: {os.path.abspath(image_file)}")

        # Load the original image using PIL
        try:
            image = Image.open(image_file)
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"이미지를 로드할 수 없습니다: {image_file}, 오류: {e}")
            continue

        highlighted_image = image.copy()

        # Prepare the image request
        headers = {
            'X-OCR-SECRET': secret_key,
            'Content-Type': 'application/json'
        }

        # Encode image to base64
        with open(image_file, "rb") as f:
            image_content = base64.b64encode(f.read()).decode('utf-8')

        # Setting up the request JSON
        request_json = {
            'images': [
                {
                    'format': 'jpg',
                    'name': filename,
                    'data': image_content
                }
            ],
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': int(round(time.time() * 1000))
        }

        # Make the OCR request
        try:
            response = requests.post(api_url, headers=headers, json=request_json, timeout=60)

            # OCR 응답 처리
            if response.status_code == 200:
                ocr_results = response.json()
                all_texts = []
                for image_result in ocr_results['images']:
                    for field in image_result['fields']:
                        text = field['inferText']
                        all_texts.append(text)

                        # Draw rectangle around text
                        bounding_box = field['boundingPoly']['vertices']
                        start_point = (int(bounding_box[0]['x']), int(bounding_box[0]['y']))
                        end_point = (int(bounding_box[2]['x']), int(bounding_box[2]['y']))
                        cv2.rectangle(highlighted_image, start_point, end_point, (0, 0, 255), 2)

                print(f"Results for {filename}:")
                for text in all_texts:
                    print(text)
            else:
                print(f"OCR 결과를 받아오지 못했습니다. 상태 코드: {response.status_code} for {filename}")
                print(f"응답 내용: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"요청 중 오류 발생: {e} for {filename}")

        # Display the original and highlighted images side by side
        fig, axs = plt.subplots(1, 2, figsize=(15, 10))
        axs[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        axs[0].set_title('Original Image')
        axs[0].axis('off')

        axs[1].imshow(cv2.cvtColor(highlighted_image, cv2.COLOR_BGR2RGB))
        axs[1].set_title('Highlighted Image')
        axs[1].axis('off')

        plt.show()
