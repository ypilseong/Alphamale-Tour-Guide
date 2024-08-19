import gradio as gr
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from chat_solar.rag_gyu import UpstageRAGChatbot  # 귀하의 코드가 있는 모듈을 import
from chat_solar.naver_scraping import naver_scraping_web

# UpstageRAGChatbot 인스턴스 생성
api_key = os.getenv("UPSTAGE_API_KEY")
file_path = "data/output_with_area5.csv"
naver_client_id = os.getenv("NAVER_CLIENT_ID")
naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")

# 질문 리스트와 선택지
questions = [
    "1. 산과 바다 중 어디를 선호하시나요?",
    "2. 도심지와 자연 중 어디를 더 선호하시나요?",
    "3. 여행 시 활동적인 일정과 휴식을 위한 일정을 선호하시나요?",
    "4. 고기를 선호하시나요, 아니면 생선을 선호하시나요?",
    "5. 야경 감상을 좋아하시나요?",
    "6. 현지 음식 체험을 선호하시나요?",
    "7. 전문점 음식과 길거리 음식 중 어디를 더 선호하시나요?",
    "8. 야외활동과 실내활동 중 어느 것을 선호하시나요?"
]

choices = [
    ["산", "상관없음", "바다"],
    ["도심지", "상관없음", "자연"],
    ["활동적", "상관없음", "휴식"],
    ["고기", "상관없음", "생선"],
    ["예", "상관없음", "아니오"],
    ["예", "상관없음", "아니오"],
    ["전문점 음식", "상관없음", "길거리 음식"],
    ["야외활동", "상관없음", "실내활동"]
]

# 선택한 답변을 저장할 딕셔너리
current_selection = {question: None for question in questions}

# 선택 결과를 dict 형태로 반환하는 함수
def get_user_responses():
    return {
        "선호_환경": current_selection[questions[0]],
        "선호_지역": current_selection[questions[1]],
        "여행_스타일": current_selection[questions[2]],
        "선호_음식": current_selection[questions[3]],
        "야경_선호": current_selection[questions[4]],
        "현지_음식_체험": current_selection[questions[5]],
        "음식점_유형": current_selection[questions[6]],
        "활동_유형": current_selection[questions[7]]
    }

# Gradio 인터페이스 함수
def answer_question(question, answer):
    current_selection[question] = answer  # 선택한 항목을 저장
    result_text = "\n".join([f"{q}: {a if a is not None else '선택되지 않음'}" for q, a in current_selection.items()])
    
    # '다음' 버튼 가시성 조정
    if check_all_answered():
        return result_text, gr.update(visible=True)
    else:
        return result_text, gr.update(visible=False)

# 모든 질문에 대한 답변이 완료되었는지 확인하는 함수
def check_all_answered():
    return all(answer is not None for answer in current_selection.values())

# Chatbot 상호작용 처리
def chatbot_interaction(message):
    # message가 dict일 가능성을 배제하고 문자열로 처리
    if isinstance(message, dict):
        message = str(message)  # dict를 문자열로 변환
    
    # 사용자의 선택을 dict 형태로 생성하여 Chatbot에 전달
    user_responses = get_user_responses()
    chatbot = UpstageRAGChatbot(api_key, file_path,naver_client_id,naver_client_secret, user_responses)
    # 각 user_responses 값이 문자열로 변환되도록 확인
    user_responses = {key: (str(value) if value is not None else "상관없음") for key, value in user_responses.items()}
    
    # message와 user_responses를 사용해 chatbot의 응답 생성
    response, places = chatbot.keyword_ask(message)
    print("ChatBot:", response)
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
    chatbot.setup_guide_model_and_chain(place_info=place_info)
    response_guide = chatbot.guide_ask(message)

    # Markdown 형식으로 응답
    markdown_response = f"**ChatBot 답변**: {response_guide}\n\n"
    if place_info:
        markdown_response += "**추천 장소 정보**:\n\n"
        for place in place_info:
            markdown_response += f"- **상호명**: {place['상호명']}\n"
            markdown_response += f"  - **주소**: {place['주소']}\n"
            markdown_response += f"  - **전화번호**: {place['전화번호']}\n"
    return markdown_response

# Gradio 앱 구성
with gr.Blocks() as demo:
    output = gr.Textbox(label="선택 결과", lines=10, interactive=False)
    
    # '다음' 버튼 생성 (초기에는 비활성화 상태)
    next_button = gr.Button("다음", visible=False)

    # 질문과 버튼들 생성
    for i, question in enumerate(questions):
        with gr.Row():
            gr.Markdown(question)  # 질문 출력
        with gr.Row():
            for choice in choices[i]:
                # 버튼을 클릭할 때 선택된 항목을 저장하고 결과를 업데이트
                gr.Button(choice).click(
                    lambda q=question, c=choice: answer_question(q, c),
                    inputs=None,
                    outputs=[output, next_button]
                )
    
    # Chatbot 화면 표시
    chatbot_input = gr.Textbox(label="메시지 입력", placeholder="여행 관련 질문을 입력하세요.", visible=False)
    
    # interactive 및 visible 인자 제거
    chatbot_output = gr.Markdown(label="챗봇 응답")
    
    # '다음' 버튼 클릭 시 Chatbot 인터페이스 표시
    def show_chat_interface():
        return gr.update(visible=True), gr.update(visible=True)
    
    next_button.click(show_chat_interface, inputs=None, outputs=[chatbot_input, chatbot_output])
    
    # Chatbot 상호작용 처리
    chatbot_input.submit(chatbot_interaction, chatbot_input, chatbot_output)

demo.launch()
