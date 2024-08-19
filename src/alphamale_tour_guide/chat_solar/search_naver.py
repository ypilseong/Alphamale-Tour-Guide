import os
import urllib.request
import json
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser

class NaverBlogSearchAndExtractor:
    def __init__(self, naver_client_id, naver_client_secret, upstage_api_key):
        self.naver_client_id = naver_client_id
        self.naver_client_secret = naver_client_secret
        self.api_key = upstage_api_key
        self.setup_llm()

   # setup_llm 메서드 내에서
    def setup_llm(self):
        os.environ["OPENAI_API_KEY"] = self.api_key
        os.environ["OPENAI_API_BASE"] = "https://api.upstage.ai/v1/solar"
        self.llm = ChatOpenAI(model_name="solar-1-mini-chat", temperature=0.1)

        template = """
        너는 텍스트에서 가게 이름을 정확하고 신뢰성 있게 추출하는 전문 인공지능이야. 
        
        작업 지침:
        1. 텍스트에서 **고유한 가게 이름**만을 추출해.
        2. 가게 이름에 포함될 수 있는 일반적인 단어나 명사(예: 카페, 음식점, 레스토랑, 바, 가게 등)는 **제외**하고, 상호명을 구성하는 **고유 명사**만 남겨.
        3. 가게 이름이 여러 개일 경우, 쉼표(,)로 구분하여 나열해.
        4. 텍스트에 나열된 순서에 맞춰 추출해.
        5. 상호명에 불필요한 수식어(예: '전문점', '지점', '프랜차이즈')는 제거해.
        6. 가능한 한 원문에 가깝게 정확한 가게 이름을 유지해.
        7. 형용사로 끝나는 단어는 제거해.
        8. 가게 이름이 추출되지 않거나 텍스트에 언급되지 않았으면 제거해. 


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

    def search_and_extract(self, querys):
        all_place_names = []
        for query in querys:
            query = '제주 ' + query  # 제주도 관련 검색
            search_results = self.search_blogs(query, start=1, display=10)
            if search_results:
                place_names = self.extract_place_names(search_results)
                all_place_names.extend(place_names)

            else:
                break
        return list(set(all_place_names))  # 최종 중복 제거

if __name__ == '__main__':
    # 환경 변수 가져오기
    naver_client_id = os.getenv('NAVER_CLIENT_ID')
    naver_client_secret = os.getenv('NAVER_CLIENT_SECRET')
    upstage_api_key = os.getenv('UPSTAGE_API_KEY')

    # 환경 변수들이 모두 제대로 설정되어 있는지 확인
    if not naver_client_id or not naver_client_secret or not upstage_api_key:
        print("NAVER Client ID, Secret 또는 OpenAI API Key가 설정되지 않았습니다.")
    else:
        searcher = NaverBlogSearchAndExtractor(naver_client_id, naver_client_secret, upstage_api_key)
        keyword = '길거리 음식, 바다가 보이는 카페'
        results = searcher.search_and_extract(keyword.split(','))
        print('추출된 장소 이름２: ')
        for place in results:
            print(f'- {place}')
