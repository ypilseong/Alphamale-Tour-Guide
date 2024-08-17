import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

class UpstageRAGChatbot:
    def __init__(self, api_key, file_path):
        self.api_key = api_key
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

        {context}

        질문: {question}
        대답: """
        QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "question"], template=template)

        self.qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=self.vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
        )

    def ask(self, question):
        result = self.qa_chain({"query": question})
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
    file_path = "data/output.csv"
    
    chatbot = UpstageRAGChatbot(api_key, file_path)
    chatbot.chat()