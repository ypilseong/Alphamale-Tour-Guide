import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from chat_solar.search_naver import NaverBlogSearchAndExtractor
from chat_solar.naver_scraping import naver_scraping_web
import torch
torch.cuda.empty_cache()


class UpstageRAGChatbot:
    def __init__(self, api_key, file_path, naver_client_id, naver_client_secret,user_responses={
            "선호_환경": "산",
            "선호_지역": "자연",
            "여행_스타일": "활동적",
            "선호_음식": "고기",
            "야경_선호": "예",
            "현지_음식_체험": "예",
            "음식점_유형": "길거리 음식",
            "활동_유형": "야외활동"
        }):
        self.answer1 = user_responses["선호_환경"]
        self.answer2 = user_responses["선호_지역"]
        self.answer3 = user_responses["여행_스타일"]
        self.answer4 = user_responses["선호_음식"]
        self.answer5 = user_responses["야경_선호"]
        self.answer6 = user_responses["현지_음식_체험"]
        self.answer7 = user_responses["음식점_유형"]
        self.answer8 = user_responses["활동_유형"]
        self.api_key = api_key
        self.naver_client_id = naver_client_id
        self.naver_client_secret = naver_client_secret
        self.file_path = file_path
        self.setup_environment()
        self.load_and_process_documents()
        self.setup_keyword_model_and_chain()

    def setup_environment(self):
        os.environ["OPENAI_API_KEY"] = self.api_key
        os.environ["OPENAI_API_BASE"] = "https://api.upstage.ai/v1/solar"

    def load_and_process_documents(self):
        loader = CSVLoader(file_path=self.file_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)

        embeddings = HuggingFaceBgeEmbeddings()
        self.vectorstore = FAISS.from_documents(texts, embeddings)

    def setup_keyword_model_and_chain(self):
        self.llm = ChatOpenAI(
            model_name="solar-1-mini-chat",
            temperature=0.1,
            max_tokens=3000
        )
        

# 친구랑 둘이 4월 말에 제주도에 2박3일로 가려 해. 일출을 볼 수 있는 장소와 바다를 볼 수 있는 좋은 카페들 추천해줘. 흑돼지와 갈치구이 먹는 것도 꼭 포함해서 일정 만들어줘. 예산은 1인당 50만원 이내로 부탁해.

        


        keyword_template = """당신은 사용자의 질문에서 특징에 해당하는 키워드를 찾는 역할이다. 사용자의 질문에서 특징에 해당하는 키워드를 찾아.

        {context}

        """
        keyword_template +=  """
        사용자의 질문(input)에서 특징에 해당하는 키워드를 찾으세요.
        예를들어 '바다가 보이는 카페, 일출을 볼 수 있는 장소, 사람이 많이 없는곳, 바다를 볼 수 있는 좋은 카페, 경치 좋은 카페'같은 말을 [사용자가 원하는 특징 키워드]로 지정해.
        
        반드시 다음과 같은 형식으로 대답하세요:
        일정: [일정 키워드]
        예산: [예산 키워드]
        사용자가 원하는 특징: [사용자가 원하는 특징 키워드]

        질문: {question}
        대답: """

        
        self.keyword_prompt = PromptTemplate.from_template(keyword_template)

        self.retriever = self.vectorstore.as_retriever()

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        
        self.keyword_rag_chain = (
            {
                "context": self.retriever | format_docs, 
                "question": RunnablePassthrough()
            }
            | self.keyword_prompt
            | self.llm
            | StrOutputParser()
        )

    def setup_guide_model_and_chain(self, place_info):
        # place_info 딕셔너리를 문자열로 변환
        place_info_str = "\n".join(
            f"상호명: {info.get('상호명', 'N/A')}, 주소: {info.get('주소', 'N/A')}, 전화번호: {info.get('전화번호', 'N/A')}"
            for info in place_info
        )
        
        guide_template = """당신은 친절한 가이드입니다. 여행자가 물어보는 질문에 대답해주세요. 모든 정보는 대한민국 제주도에 해당하는 정보로 대답해주세요.

        {context}

        """
        guide_template += f"""
        사용자의 선호도:
        1. 산과 바다 중 어디를 선호하시나요? : {self.answer1}
        2. 도심지와 자연 중 어디를 더 선호하시나요? : {self.answer2}
        3. 여행 시 활동적인 일정과 휴식을 위한 일정을 선호하시나요? : {self.answer3}
        4. 고기를 선호하시나요, 아니면 생선을 선호하시나요? : {self.answer4}
        5. 야경 감상을 좋아하시나요? : {self.answer5}
        6. 현지 음식 체험을 선호하시나요? : {self.answer6}
        7. 전문점 음식과 길거리 음식 중 어디를 더 선호하시나요? : {self.answer7}
        8. 야외활동과 실내활동 중 어느 것을 선호하시나요? : {self.answer8}
        """
        # place_info 추가
        guide_template += f"""
        추천된 장소 정보:
        {place_info_str}
        반드시 추천된 장소를 기반으로 일정을 계획하세요.
        """
        guide_template +="""
        세부 가이드라인:
        1. 일정은 반드시 제공된 장소를 기반으로 구성하되, 만약 주소가 제공되지 않은 장소가 있다면, 해당 장소는 제외하고 다른 적절한 장소로 대체하세요.
        2. 장소의 이름은 구체적으로 명시하세요. 예를 들어 '카페'나 '음식점' 같은 포괄적인 용어와 '점심 식사'나 '저녁 식사' 같은 단어 대신, 구체적인 상호명을 사용하세요.
        3. 만약 추천된 장소 중에서 대체할 장소가 부족할 경우, 추가 검색을 통해 주소와 세부 정보를 갖춘 새로운 장소를 찾아 추가하세요.
        4. 일정은 하루 단위로 나누어 아침, 점심, 저녁 활동과 휴식 시간을 균형 있게 포함시키세요.
        5. 일정에 대한 설명은 간결하고 명확하게, 시간대에 맞는 활동을 추천하세요. 예를 들어, 아침엔 산책이나 일출 명소, 점심엔 현지 맛집, 저녁엔 일몰을 감상할 수 있는 장소를 포함하세요.
        6. 일정 내 모든 추천된 장소의 세부 주소를 반드시 포함시키고, 장소마다 간단한 추천 팁을 제공하세요. 예를 들어 가장 붐비는 시간대나 현지 주민들이 주로 방문하는 숨겨진 명소 등의 정보를 제공하세요.

        세부 정보 제공:
        각 장소에 대한 기본 정보와 추천 이유를 간단히 설명하세요. 예를 들어, “성산일출봉: 제주도의 대표적인 일출 명소로, 자연 경관이 아름답고 가벼운 등산을 즐길 수 있습니다.”와 같은 짧은 설명을 포함하세요.
        모든 일정에 '추천 팁'을 반드시 포함시키세요: 각 장소나 활동에 대해 추천 팁을 제공하세요. 예를 들어, 가장 붐비는 시간대나 현지 주민들이 주로 방문하는 숨겨진 명소 등을 알려주는 방식으로 여행자를 도와주세요.

        세부 주소 제공:
        모든 추천된 장소는 반드시 주소가 명확하게 표시되어야 합니다. 만약 주소가 명확하지 않은 장소가 추천되었다면, 해당 장소는 제외하고 다른 것으로 대체하세요.
        예를 들어:

        n일차        
        | 시간 | 장소 | 상세 내용 | 예상 비용 (1인) | 주소 |
        | --- | --- | --- | --- | --- |
        | 09:00 | a | b | c | d |
        | 10:00 ~ 11:30 | X | Y | Z | A |

        이러한 형식으로 일정을 구성하세요.
        장소 이름은 상호명을 사용하고, 포괄적인 단어로 언급하지 마세요. 예를 들어 '카페', '음식점', '숙소' 대신, 구체적인 상호명을 사용하세요.

        추가로 반드시 일정 내 모든 장소의 주소만 따로 정리하세요.
        예를 들어:
        1일차 주소: 주소1, 주소2, 주소3, ...
        2일차 주소: 주소1, 주소2, 주소3, ...
        반드시 모든 형식의 맞춰서 답변을 해주세요.

        질문: {question}
        대답: """
        
        self.guide_prompt = PromptTemplate.from_template(guide_template)

        self.retriever = self.vectorstore.as_retriever()

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        guide_template = PromptTemplate.from_template(guide_template)

        # 장소 정보 리스트를 각각 전달하도록 수정
        self.guide_rag_chain = (
            {
                "context": self.retriever | format_docs, 
                "question": RunnablePassthrough()
            }
            | self.guide_prompt
            | self.llm
            | StrOutputParser()
        )

    
    def keyword_ask(self, question):
        result = self.keyword_rag_chain.invoke(question)
        features = self.extract_user_features(result)
        place_names = self.search_places(features)
        return result, place_names
    
    def guide_ask(self, question):
        result = self.guide_rag_chain.invoke(question)
        return result
    
    def LLM_address_extract():
        pass


    def extract_user_features(self, response):
        # '사용자가 원하는 특징: ' 문자열 이후의 텍스트를 추출
        start_index = response.find("사용자가 원하는 특징: ")
        if start_index != -1:
            features = response[start_index + len("사용자가 원하는 특징: "):].strip()
            return features
        return ""
    
    def search_places(self, features):
        # 네이버 블로그 검색 및 추출기 인스턴스 생성
        searcher = NaverBlogSearchAndExtractor(self.naver_client_id, self.naver_client_secret, self.api_key)
        
        # 추출된 특징 키워드를 네이버 블로그 검색에 사용
        results = searcher.search_and_extract([features])
        
        return results
    
    def chat(self):
        print("Chatbot: 안녕하세요! 어떤 도움이 필요하신가요? ('quit'을 입력하면 종료됩니다)")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Chatbot: 안녕히 가세요!")
                break
            
            response, places = self.keyword_ask(user_input)
            print("Chatbot:", response)
            if places:
                print("추출된 장소 이름:", ', '.join(places))
            else:
                print("추출된 장소 이름이 없습니다.")
            
            place_info = []
            for place in places:
                place.replace("제주","")
                shop_name, address, phone_number = naver_scraping_web(place)
                place_detail = {"상호명": shop_name, "주소": address, "전화번호": phone_number}
                if shop_name == "상호명 없음":
                    pass
                else:
                    print("상호명:", shop_name)
                    print("주소:", address)
                    print("전화번호:", phone_number)
                    place_info.append(place_detail)
            self.setup_guide_model_and_chain(place_info)
            response_gudie = self.guide_ask(user_input)
            print("Chatbot:", response_gudie)
        return response_gudie
# 사용 예시
if __name__ == "__main__":
    api_key = os.getenv("UPSTAGE_API_KEY")
    naver_client_id = os.getenv('NAVER_CLIENT_ID')
    naver_client_secret = os.getenv('NAVER_CLIENT_SECRET')
    file_path = "data/output_with_area5.csv"
    
    chatbot = UpstageRAGChatbot(api_key, file_path, naver_client_id, naver_client_secret)
    chatbot.chat()