from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# Wit.ai 서버 토큰
WIT_API_TOKEN = 'TBCO7P3553JLIA3FQYYMJHQE2JYYMQNH'

# 시범이가 보내준 데이터 불러오기
def load_students():
    with open("static/data/students.json", encoding="utf-8") as f:
        data = json.load(f)
    students = data["student_id"]
    number_to_name = {s["Id"]: s["Name"] for s in students}
    name_to_number = {s["Name"]: s["Id"] for s in students}
    return number_to_name, name_to_number

number_to_name, name_to_number = load_students()

# Wit.ai intent 분석
def get_wit_response(text):
    url = 'https://api.wit.ai/message'
    headers = {
        'Authorization': f'Bearer {WIT_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    params = {'q': text, 'v': '20250714'}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 메인 페이지 라우팅
@app.route("/")
def index():
    return render_template("index.html")

# 질문에 응답해주는 api
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("text", "")

    wit_data = get_wit_response(user_input)
    intent = wit_data.get("intents", [{}])[0].get("name", "")
    entities = wit_data.get("entities", {})

    # intent 처리해주는 부분
    if intent == "get_teacher_name":
        answer = "우리 반 담임 선생님은 장세민 선생님이야!"

    elif intent == "get_student_name":
        number_entity = entities.get("student_number:student_number", [{}])[0].get("value")
        if number_entity:
            full_number = f"310{int(number_entity):02d}"
            student_name = number_to_name.get(full_number)
            if student_name:
                answer = f"{number_entity}번 학생은 {student_name}이야!"
            else:
                answer = f"{number_entity}번? 그 번호를 가진 학생은 없는 것 같아!"
        else:
            answer = "몇 번인지 잘 못 들었어!"

    elif intent == "get_student_number":
        name_entity = entities.get("student_name:student_name", [{}])[0].get("value")
        if name_entity:
            student_number = name_to_number.get(name_entity)
            if student_number:
                answer = f"{name_entity}의 학번은 {student_number}이야!"
            else:
                answer = f"{name_entity}? 그 이름은 잘 모르겠어ㅠㅠ"
        else:
            answer = "누구의 학번인지 잘 못 들었어!"

    else:
        answer = "음... 질문을 잘 이해하지 못했어"

    return jsonify({"answer": answer})

# 실행 코드
if __name__ == "__main__":
    app.run(debug=True)
