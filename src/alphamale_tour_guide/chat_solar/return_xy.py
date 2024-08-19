import requests
import re
import os
import time

vworld_api_key = os.getenv('VWORLD_API_KEY')

# API 호출 함수
def get_coordinates(address, address_type="road"):
    apiurl = "https://api.vworld.kr/req/address?"
    params = {
        "service": "address",
        "request": "getcoord",
        "crs": "epsg:4326",
        "address": address,
        "format": "json",
        "type": address_type,  # "road" for 도로명, "parcel" for 지번
        "key": vworld_api_key
    }
    response = requests.get(apiurl, params=params)
    if response.status_code == 200:
        result = response.json()
        if result['response']['status'] == 'OK':
            x = result['response']['result']['point']['x']
            y = result['response']['result']['point']['y']
            return float(x), float(y)  # 문자열을 float으로 변환
    return None, None

# 주소 리스트를 경위도로 변환하는 함수
def get_coordinates_list(address_list):
    coordinates_list = []
    for address in address_list:
        # 먼저 도로명 주소로 시도
        lon, lat = get_coordinates(address, address_type="road")
        if not lon or not lat:
            # 도로명 주소 실패 시, 지번 주소로 재시도
            lon, lat = get_coordinates(address, address_type="parcel")
        
        if lon and lat:
            coordinates_list.append((lat, lon))
        else:
            coordinates_list.append((None, None))
        
        time.sleep(0.1)  # API 요청 간 간격 조절
    
    return coordinates_list

# 주어진 텍스트에서 주소를 추출하는 함수
def extract_addresses(text):
    # 1일차와 2일차 주소 패턴을 찾기 위한 정규 표현식
    day1_pattern = r"1일차 주소:\s*(.*?)\s*2일차 주소:"
    day2_pattern = r"2일차 주소:\s*(.*?)$"

    # 1일차 주소 추출
    day1_match = re.search(day1_pattern, text, re.DOTALL)
    day1_addresses = []
    if day1_match:
        day1_addresses = day1_match.group(1).strip().split("\n")
        day1_addresses = [re.sub(r"^[^:]+:\s*", "", address.strip()) for address in day1_addresses if address.strip()]

    # 2일차 주소 추출
    day2_match = re.search(day2_pattern, text, re.DOTALL)
    day2_addresses = []
    if day2_match:
        day2_addresses = day2_match.group(1).strip().split("\n")
        day2_addresses = [re.sub(r"^[^:]+:\s*", "", address.strip()) for address in day2_addresses if address.strip()]

    return day1_addresses, day2_addresses

# 주어진 텍스트에서 주소를 추출하고, 경위도 리스트 반환
def get_coordinates_for_days(text):
    day1_addresses, day2_addresses = extract_addresses(text)
    
    # 1일차와 2일차 주소를 경위도로 변환
    day1_coordinates = get_coordinates_list(day1_addresses)
    day2_coordinates = get_coordinates_list(day2_addresses)
    
    return day1_coordinates, day2_coordinates

if __name__ == '__main__':
    # 테스트용 텍스트
    text = """
    주소 정리
    1일차 주소:

    에코승마아카데미: 제주시 조천읍 비자림로 1065
    함덕해수욕장: 제주시 조천읍 함덕리 1008-4
    해녀의 집: 제주시 구좌읍 해맞이해안로 1282
    월정리 해변: 제주시 구좌읍 월정리 33-3
    김녕해수욕장: 제주시 구좌읍 김녕리 522-1
    제주 흑돼지 거리: 제주시 연동 2316-3
    숙소: 제주시 연동 1234-5
    2일차 주소:

    숙소: 제주시 연동 1234-5
    신라면세점 제주점: 제주시 노연로 69
    돈사돈: 제주시 연동 272-18
    이호테우 해변: 제주시 이호일동 2541-1
    워너비제주: 제주시 구좌읍 행원로9길 8-1
    제주국제공항: 제주시 용담2동 2002-1
    """

    # 주소 추출 및 경위도 리스트 반환
    day1_coordinates, day2_coordinates = get_coordinates_for_days(text)

    print("1일차 경위도 리스트:", day1_coordinates)
    print("2일차 경위도 리스트:", day2_coordinates)
