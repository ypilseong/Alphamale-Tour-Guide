import requests
from bs4 import BeautifulSoup

def naver_scraping_web(place_name):
    place_name += '제주 '
    place_name.replace(" ", "+")
    # 검색 결과 페이지 URL
    url = f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={place_name}"

    # requests로 페이지 가져오기
    response = requests.get(url)

    # 페이지 파싱하기
    soup = BeautifulSoup(response.text, 'html.parser')

    # 상호명 추출
    shop_name_element = soup.select_one("#_title > a > span.GHAhO")
    shop_name = shop_name_element.text if shop_name_element else "상호명 없음"

    # 주소 추출
    "#place-main-section-root > section > div > div:nth-child(3) > div.place_section_content > div > div.O8qbU.tQY7D.AoRCe > div > a > span.LDgIH"
    address_element = soup.select_one("#place-main-section-root > section > div > div:nth-child(2) > div.place_section_content > div > div.O8qbU.tQY7D.AoRCe > div > a > span.LDgIH")
    if address_element:
        address = address_element.text
    elif address_element is None:
        try:
            address_element = soup.select_one("#place-main-section-root > div > section > div > div:nth-child(3) > div > div > div.O8qbU.tQY7D.AoRCe > div > a > span.LDgIH")
            address = address_element.text
        except:
            address_element = soup.select_one("#place-main-section-root > section > div > div:nth-child(3) > div > div > div.O8qbU.tQY7D.AoRCe > div > a > span.LDgIH")
            address = address_element.text if address_element else "주소 없음"

    # 전화번호 추출
    phone_number_element = soup.select_one("#place-main-section-root > section > div > div:nth-child(2) > div.place_section_content > div > div.O8qbU.nbXkr.AoRCe > div > span")
    if phone_number_element:
        phone_number = phone_number_element.text
    elif phone_number_element is None:
        try:
            phone_number_element = soup.select_one("#place-main-section-root > section > div > div:nth-child(3) > div.place_section_content > div > div.O8qbU.nbXkr.AoRCe > div > span")
            phone_number = phone_number_element.text
        except:
            phone_number_element = soup.select_one("#place-main-section-root > div > section > div > div:nth-child(3) > div > div > div.O8qbU.nbXkr.AoRCe > div > span")
            phone_number = phone_number_element.text if phone_number_element else "전화번호 없음"
    #place-main-section-root > section > div > div:nth-child(3) > div.place_section_content > div > div.O8qbU.nbXkr.AoRCe > div > span
    #place-main-section-root > div > section > div > div:nth-child(3) > div > div > div.O8qbU.nbXkr.AoRCe > div > span
    ##place-main-section-root > section > div > div:nth-child(3) > div.place_section_content > div > div.O8qbU.nbXkr.AoRCe > div > span
    # 결과 출력
    

    return shop_name, address, phone_number

if __name__ == "__main__":
    naver_scraping_web("제주도 일출명소")