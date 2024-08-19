import gradio as gr
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from chat_solar.rag_chatbot import UpstageRAGChatbot
from chat_solar.naver_scraping import naver_scraping_web
from chat_solar.return_xy import get_coordinates_for_days
from route_opt.route_optimization import route_optimization

# UpstageRAGChatbot 인스턴스 생성
upstage_api_key = os.getenv("UPSTAGE_API_KEY")
naver_client_id = os.getenv("NAVER_CLIENT_ID")
naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")

file_path = "data/output_with_area5.csv"

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
    if isinstance(message, dict):
        message = str(message)
    
    user_responses = get_user_responses()
    chatbot = UpstageRAGChatbot(upstage_api_key, file_path, naver_client_id, naver_client_secret, user_responses)
    user_responses = {key: (str(value) if value is not None else "상관없음") for key, value in user_responses.items()}
    
    response, places = chatbot.keyword_ask(message)
    place_info = []
    for place in places:
        place.replace("제주","")
        shop_name, address, phone_number = naver_scraping_web(place)
        place_detail = {"상호명": shop_name, "주소": address, "전화번호": phone_number}
        if shop_name == "상호명 없음":
            pass
        else:
            place_info.append(place_detail)
    
    chatbot.setup_guide_model_and_chain(place_info=place_info)
    response_guide = chatbot.guide_ask(message)
    
    return response_guide

def optimize_route(response_guide):
    day1_coordinates, day2_coordinates = get_coordinates_for_days(response_guide)
    days_coordinates = {1: day1_coordinates, 2: day2_coordinates}
    route_optimization(days_coordinates)
    dir_path="/home/a202121010/workspace/projects/Alphamale-Tour-Guide/src/alphamale_tour_guide/gradio"
    print(days_coordinates)
    terminal_command = f"cd {dir_path}"
    os.system(terminal_command)
    terminal_command2 = f"python3 -m http.server 8000"
    os.system(terminal_command2)
    print('완료')
    return "경로 최적화가 완료되었습니다."

# Gradio 앱 구성
with gr.Blocks() as demo:
    output = gr.Textbox(label="선택 결과", lines=10, interactive=False)
    next_button = gr.Button("다음", visible=False)

    for i, question in enumerate(questions):
        with gr.Row():
            gr.Markdown(question)
        with gr.Row():
            for choice in choices[i]:
                gr.Button(choice).click(
                    lambda q=question, c=choice: answer_question(q, c),
                    inputs=None,
                    outputs=[output, next_button]
                )
    
    chatbot_input = gr.Textbox(label="메시지 입력", placeholder="여행 관련 질문을 입력하세요.", visible=False)
    chatbot_output = gr.Markdown(label="챗봇 응답")
    
    def show_chat_interface():
        return gr.update(visible=True), gr.update(visible=True)
    
    next_button.click(show_chat_interface, inputs=None, outputs=[chatbot_input, chatbot_output])
    
    chatbot_input.submit(chatbot_interaction, chatbot_input, chatbot_output)
    
    optimize_button = gr.Button("경로 최적화", visible=True)
    optimize_button.click(optimize_route, inputs=chatbot_output, outputs=chatbot_output)

    naver_html = gr.HTML('''
        <button onclick="window.open('http://localhost:8000/src/alphamale_tour_guide/route_opt/', '_blank');">
            경로 결과 확인
        </button>
    ''')
    
demo.launch()
