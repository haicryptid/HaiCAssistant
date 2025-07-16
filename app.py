from flask import Flask, render_template, request, jsonify
import requests
import json
import re

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

# 시간표 데이터 불러오기(여기도 새로 추가된 부분임!)
def load_timetable():
    with open("static/data/timeTable.json", encoding="utf-8") as f:
        data = json.load(f)
    week_data = data["week"]
    time_table = {}
    for day_object in week_data:
        for weekday_key, periods in day_object.items():
            time_table[weekday_key] = periods[0]
    return time_table

time_table = load_timetable()



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

    # 학번 제대로 읽게 함
    elif intent == "get_student_number":
        name_entity = entities.get("student_name:student_name", [{}])[0].get("value")
        if name_entity:
            student_number = name_to_number.get(name_entity)
            if student_number:
                student_number_space = ' '.join(student_number)
                answer = f"{name_entity}의 학번은 {student_number_space}야!"
            else:
                answer = f"{name_entity}? 그 이름은 잘 모르겠어ㅠㅠ"
        else:
            answer = "누구의 학번인지 잘 못 들었어!"

    # 이 부분 추가함(여기부터 시간표 응답 로직)

    elif intent == "get_subject_by_time":
        weekday_entity = entities.get("weekday:weekday", [{}])[0].get("value")
        time_entity = entities.get("time:time", [{}])[0].get("value")

        if weekday_entity and time_entity:
        # 한글 요일 → JSON 키로 변환
            day_map = {
                "월요일": "Mon", "화요일": "Tue", "수요일": "Wed",
                "목요일": "Thu", "금요일": "Fri"
            }

            match = re.search(r'\d+', time_entity)
            time_num = match.group() if match else None

            weekday_eng = day_map.get(weekday_entity)

            if weekday_eng and time_num and f"{time_num}c" in time_table[weekday_eng]:
                subject = time_table[weekday_eng][f"{time_num}c"]
                answer = f"{weekday_entity} {time_num}교시는 {subject}야!"
            else:
                answer = f"{weekday_entity} {time_entity}는 수업이 없는 것 같아!"
        else:
            answer = "요일이나 교시 정보를 잘 못 들었어!"

    else:
        answer = "음... 질문을 잘 이해하지 못했어"

    return jsonify({"answer": answer})

# 실행 코드
if __name__ == "__main__":
    app.run(debug=True)
