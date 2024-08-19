import os
import urllib.request
import json
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser


class NaverBlogSearchAndExtractor:
    def __init__(self, naver_client_id, naver_client_secret, openai_api_key):
        self.naver_client_id = naver_client_id
        self.naver_client_secret = naver_client_secret
        self.openai_api_key = openai_api_key
        self.setup_llm()

    # setup_llm 메서드 내에서
    def setup_llm(self):
        os.environ["OPENAI_API_KEY"] = self.openai_api_key
        os.environ["OPENAI_API_BASE"] = "https://api.upstage.ai/v1/solar"
        self.llm = ChatOpenAI(model_name="solar-1-mini-chat", temperature=0.1)

        template = """
        너는 텍스트에서 가게 이름만을 정확하게 추출하는 인공지능이야. 다음 지침을 엄격하게 따라. 만약 따르지 않으면 넌 해고야.
        
        작업 지침:
        1. 텍스트에서 가게 이름으로 추정되지 않는 일반적인 문구(예: "바다가 보이는", "제주 바다 보이는" 등)은 추출하지 마.
        2. 가게 이름이 아닌 일반 명사(예: 음식, 길거리 음식, 카페, 시장 등)와 수식어(예: "제주 바다가 보이는" 등)는 반드시 제외해.
        3. 가게 이름은 고유 명사 또는 상호로 구성된 단어만 남겨. 예를 들어, "제주 바다가 보이는 카페"가 주어진 경우 카페 이름을 제외하고 일반적인 묘사는 추출하지 마.
        4. 상호명이 아닌 메뉴 이름(예: 흑돼지 철판구이, 빵돼구이, 킹크랩, 랍스터 등)은 제외해.
        5. 추출된 가게 이름이 불완전하거나, 고유 명사로 확신할 수 없으면 공백으로 두어라.
        6. 여러 개의 가게 이름이 있을 경우, 쉼표(,)로 구분해.

        텍스트: {text}

        가게 이름:
        """



        self.prompt = PromptTemplate(template=template, input_variables=["text"])
        
        # 파이프라인 연산자를 사용하여 체인 구성
        self.chain = self.prompt | self.llm | StrOutputParser()

    def search_blogs(self, query, start=1, display=5):
        encText = urllib.parse.quote(query)
        url = f"https://openapi.naver.com/v1/search/blog?query={encText}&start={start}&display={display}"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.naver_client_id)
        request.add_header("X-Naver-Client-Secret", self.naver_client_secret)
        
        try:
            with urllib.request.urlopen(request) as response:
                rescode = response.getcode()
                if rescode == 200:
                    response_body = response.read().decode('utf-8')
                    return json.loads(response_body)
                else:
                    print(f"Error Code: {rescode} - 네이버 API 요청이 실패했습니다.")
                    return None
        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
        except Exception as e:
            print(f"Unexpected Error: {str(e)}")
        return None

    def extract_place_names(self, search_results):
        if not search_results or 'items' not in search_results:
            return []

        place_names = []
        for item in search_results['items']:
            title = item.get('title', '')
            description = item.get('description', '')
            full_text = f"{title} {description}"
            
            # Solar LLM을 사용하여 장소 이름 추출
            result = self.chain.invoke(full_text)
            if result:
                place_names.extend([name.strip() for name in result.split(',')])

        return list(set(place_names))  # 중복 제거

    def save_to_json(self, data, filename='search_results.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"데이터가 {filename} 파일에 저장되었습니다.")

    def search_and_extract(self, querys):
        all_place_names = []
        for query in querys:
            query = '제주 ' + query  # 제주도 관련 검색
            search_results = self.search_blogs(query, start=1, display=10)
            
            # 검색 결과를 JSON으로 저장하는 부분
            if search_results:
                self.save_to_json(search_results, filename=f'search_results_{query}.json')

                place_names = self.extract_place_names(search_results)
                all_place_names.extend(place_names)

            else:
                break
        return list(set(all_place_names))  # 최종 중복 제거

# # 사용 예시
# if __name__ == '__main__':
#     naver_client_id = os.getenv('NAVER_CLIENT_ID')
#     naver_client_secret = os.getenv('NAVER_CLIENT_SECRET')
#     openai_api_key = os.getenv('UPSTAGE_API_KEY')
    
#     # if not naver_client_id or not naver_client_secret or not openai_api_key:
#     #     print('Please set NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, and UPSTAGE_API_KEY environment variables.')
#     # else:
#     searcher = NaverBlogSearchAndExtractor(naver_client_id, naver_client_secret, openai_api_key)
#     keyword = '길거리 음식'
#     results = searcher.search_and_extract(keyword)
#     print('추출된 장소 이름: ')
#     for place in results:
#         print(f'- {place}')


if __name__ == '__main__':
    # 환경 변수 가져오기
    naver_client_id = os.getenv('NAVER_CLIENT_ID')
    naver_client_secret = os.getenv('NAVER_CLIENT_SECRET')
    openai_api_key = os.getenv('UPSTAGE_API_KEY')

    # 환경 변수 각각 출력
    print(f"NAVER_CLIENT_ID: {naver_client_id}")
    print(f"NAVER_CLIENT_SECRET: {naver_client_secret}")
    print(f"UPSTAGE_API_KEY: {openai_api_key}")

    # 환경 변수들이 모두 제대로 설정되어 있는지 확인
    if not naver_client_id or not naver_client_secret or not openai_api_key:
        print("NAVER Client ID, Secret 또는 OpenAI API Key가 설정되지 않았습니다.")
    else:
        searcher = NaverBlogSearchAndExtractor(naver_client_id, naver_client_secret, openai_api_key)
        keyword = '길거리 음식, 바다가 보이는 카페'
        results = searcher.search_and_extract(keyword.split(','))
        print('추출된 장소 이름: ')
        for place in results:
            print(f'- {place}')
