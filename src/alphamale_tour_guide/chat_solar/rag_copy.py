import re
import json

def LLM_address_extract(llm_output):
    # "주소" 필드를 추출하는 정규식 (연속된 줄바꿈을 처리)
    address_pattern = r'\| 주소 \|\n(?:\|.*?\|.*?\|.*?\|.*?\| (.*?) \|\n\n)+'
    
    # 정규식을 사용하여 모든 주소를 추출
    addresses = re.findall(address_pattern, llm_output)
    
    # 추출된 주소들을 JSON 파일로 저장
    with open("extracted_addresses.json", "w", encoding="utf-8") as f:
        json.dump(addresses, f, ensure_ascii=False, indent=4)

    print("주소가 extracted_addresses.json 파일로 저장되었습니다.")
    return addresses

# LLM 출력 예시
llm_output = """
Day 3:

| 시간 | 장소 | 상세 내용 | 예상 비용 (1인) | 주소 |
| --- | --- | --- | --- | --- |
| 09:00 | 우도 | 우도 여행 | 20,000원 | 제주 제주시 우도면 |

| 12:00 | 점심 | 해산물 요리 전문점 | 30,000원 | 제주 제주시 우도면 |

| 14:00 | 우도봉 | 우도봉에서 경치 감상 | 무료 | 제주 제주시 우도면 연평리 |

| 17:00 | 저녁 | 흑돼지 전문점 | 40,000원 | 제주 제주시 우도면 |


Day 4:

| 시간 | 장소 | 상세 내용 | 예상 비용 (1인) | 주소 |
| --- | --- | --- | --- | --- |
| 09:00 | 성산일출봉 | 성산일출봉 등산 | 5,000원 | 제주 서귀포시 성산읍 성산리 1 |

| 12:00 | 점심 | 해산물 요리 전문점 | 30,000원 | 제주 서귀포시 성산읍 성산리 1 |

| 14:00 | 아쿠아플라넷 제주 | 아쿠아리움 관람 | 40,000원 | 제주 서귀포시 성산읍 섭지코지로 95 |

| 17:00 | 저녁 | 흑돼지 전문점 | 40,000원 | 제주 서귀포시 성산읍 성산리 1 |

"""

# 함수 실행 예시
addresses = LLM_address_extract(llm_output)
print("추출된 주소:", addresses)
