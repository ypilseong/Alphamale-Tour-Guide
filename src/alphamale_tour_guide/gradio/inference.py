import gradio as gr
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from chat_solar.rag import UpstageRAGChatbot  # 귀하의 코드가 있는 모듈을 import



# UpstageRAGChatbot 인스턴스 생성
api_key = os.getenv("UPSTAGE_API_KEY")
naver_client_id = os.getenv("NAVER_CLIENT_ID")
naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")
file_path = "data/output_with_area2.csv"

chatbot = UpstageRAGChatbot(api_key, file_path)

def chat_response(message, history):
    response = chatbot.ask(message)
    return response

# Gradio 인터페이스 생성
iface = gr.ChatInterface(
    fn=chat_response,
    title="Upstage RAG Chatbot",
    description="여행 관련 질문을 해주세요. 장소는 쉼표로 구분하여 입력해주세요.",
    examples=[
        "서울, 부산에 대해 알려줘",
        "제주도의 유명한 관광지는 어디인가요?",
        "강원도, 속초의 맛집 추천해줘"
    ],
    theme=gr.themes.Soft()
)

# 애플리케이션 실행
iface.launch()