import pandas as pd
import requests
import time
import os

vworld_api_key = os.getenv('VWORLD_API_KEY')

# API 호출 함수
def get_coordinates(address):
    apiurl = "https://api.vworld.kr/req/address?"
    params = {
        "service": "address",
        "request": "getcoord",
        "crs": "epsg:4326",
        "address": address,
        "format": "json",
        "type": "parcel",
        "key": vworld_api_key
    }
    response = requests.get(apiurl, params=params)
    if response.status_code == 200:
        result = response.json()
        if result['response']['status'] == 'OK':
            x = result['response']['result']['point']['x']
            y = result['response']['result']['point']['y']
            return x, y
    return None, None

# CSV 파일 로드
file_path = 'data/output_with_area3.csv'  # CSV 파일 경로
data = pd.read_csv(file_path)

# '제주특별자치도' 제거 및 경위도 계산
data['ADDR'] = data['ADDR'].str.replace('제주특별자치도', '').str.strip()

# LON과 LAT이 없는 데이터만 처리
for index, row in data.iterrows():
    if pd.isna(row['LON']) or pd.isna(row['LAT']) or row['LON'] == '' or row['LAT'] == '':
        lon, lat = get_coordinates(row['ADDR'])
        data.at[index, 'LON'] = lon
        data.at[index, 'LAT'] = lat
        time.sleep(0.1)  # API 요청 간 간격 조절

# 결과를 새 CSV 파일로 저장
output_file = 'data/output_with_area4.csv'
data.to_csv(output_file, index=False, encoding='utf-8')

print(f"처리 완료. 결과가 {output_file}에 저장되었습니다.")
