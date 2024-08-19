import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from search_naver import NaverBlogSearchAndExtractor
from naver_scraping import naver_scraping_web
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
        self.setup_model_and_chain()

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

    def setup_model_and_chain(self):
        self.llm = ChatOpenAI(
            model_name="solar-1-mini-chat",
            temperature=0.1,
            max_tokens=1000
        )

# 친구랑 둘이 4월 말에 제주도에 2박3일로 가려 해. 일출을 볼 수 있는 장소와 바다를 볼 수 있는 좋은 카페들 추천해줘. 흑돼지와 갈치구이 먹는 것도 꼭 포함해서 일정 만들어줘. 예산은 1인당 50만원 이내로 부탁해.

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
        guide_template += """
        질문: {question}
        대답: """



        keyword_template = """당신은 사용자의 질문에서 특징에 해당하는 키워드를 찾는 역할을 합니다. 사용자의 질문에서 특징에 해당하는 키워드를 찾아주세요.

        {context}

        """
        keyword_template +=  """
        사용자의 질문(input)에서 특징에 해당하는 키워드를 찾으세요.
        
        반드시 다음과 같은 형식으로 대답하세요:
        일정: [일정 키워드]
        장소: [장소 키워드]
        예산: [예산 키워드]
        사용자가 원하는 특징: [사용자가 원하는 특징 키워드]

        질문: {question}
        대답: """

        self.guide_prompt = PromptTemplate.from_template(guide_template)
        self.keyword_prompt = PromptTemplate.from_template(keyword_template)

        self.retriever = self.vectorstore.as_retriever()

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        self.guide_rag_chain = (
            {
                "context": self.retriever | format_docs, 
                "question": RunnablePassthrough()
            }
            | self.guide_prompt
            | self.llm
            | StrOutputParser()
        )
        self.keyword_rag_chain = (
            {
                "context": self.retriever | format_docs, 
                "question": RunnablePassthrough()
            }
            | self.keyword_prompt
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
                place_detail = {"상호명": {shop_name}, "주소": {address}, "전화번호": {phone_number}}
                if shop_name == "상호명 없음":
                    pass
                else:
                    print("상호명:", shop_name)
                    print("주소:", address)
                    print("전화번호:", phone_number)
                    place_info.append(place_detail)

# 사용 예시
if __name__ == "__main__":
    api_key = os.getenv("UPSTAGE_API_KEY")
    naver_client_id = os.getenv('NAVER_CLIENT_ID')
    naver_client_secret = os.getenv('NAVER_CLIENT_SECRET')
    file_path = "data/output_with_area2.csv"
    
    chatbot = UpstageRAGChatbot(api_key, file_path, naver_client_id, naver_client_secret)
    chatbot.chat()