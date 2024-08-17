import os
import requests
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

class UpstageRAGChatbot:
    def __init__(self, api_key, naver_client_id, naver_client_secret, file_path):
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
        llm = ChatOpenAI(
            model_name="solar-1-mini-chat",
            temperature=0.7,
            max_tokens=500
        )

        template = """당신은 친절한 가이드입니다. 여행자가 물어보는 질문에 대답해주세요. 

        CSV 데이터:
        {context}

        웹 검색 결과:
        {web_results}

        질문: {question}
        대답: """
        QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "web_results", "question"], template=template)

        self.qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=self.vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
        )

    def naver_search(self, query, display=1):
        url = "https://openapi.naver.com/v1/search/local.json"  # 지역 검색 API로 변경
        headers = {
            "X-Naver-Client-Id": self.naver_client_id,
            "X-Naver-Client-Secret": self.naver_client_secret
        }
        params = {
            "query": query,
            "display": display
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def extract_places(self, question):
        # 간단한 장소 추출 로직 (쉼표로 구분된 단어들을 장소로 간주)
        return [place.strip() for place in question.split(',')]

    def search_places(self, places):
        results = []
        for place in places:
            result = self.naver_search(place)
            if 'items' in result and result['items']:
                results.append(result['items'][0])  # 각 장소의 첫 번째 검색 결과만 저장
        return results

    def ask(self, question):
        # 질문에서 장소 추출
        places = self.extract_places(question)
        
        # 추출된 장소들에 대해 검색 수행
        search_results = self.search_places(places)
        
        # 검색 결과를 문자열로 변환
        parsed_results = ""
        for item in search_results:
            parsed_results += f"장소: {item['title']}\n주소: {item['address']}\n카테고리: {item['category']}\n\n"

        # CSV 기반 응답 생성 및 웹 검색 결과 통합
        result = self.qa_chain({"query": question, "web_results": parsed_results})
        return result["result"]

    def chat(self):
        print("Chatbot: 안녕하세요! 어떤 도움이 필요하신가요? ('quit'을 입력하면 종료됩니다)")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Chatbot: 안녕히 가세요!")
                break
            
            response = self.ask(user_input)
            print("Chatbot:", response)

# 사용 예시
if __name__ == "__main__":
    api_key = os.getenv("UPSTAGE_API_KEY")
    naver_client_id = os.getenv("NAVER_CLIENT_ID")
    naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")
    file_path = "data/output.csv"
    
    chatbot = UpstageRAGChatbot(api_key, naver_client_id, naver_client_secret, file_path)
    chatbot.chat()