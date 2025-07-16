from flask import Flask, render_template, request, jsonify
import requests
import json
import re
from datetime import datetime, timedelta

app = Flask(__name__)

# Wit.ai 서버 토큰
WIT_API_TOKEN = 'TBCO7P3553JLIA3FQYYMJHQE2JYYMQNH'

# 학생 정보 불러오기
def load_students():
    with open("static/data/students.json", encoding="utf-8") as f:
        data = json.load(f)
    students = data["student_id"]
    number_to_name = {s["Id"]: s["Name"] for s in students}
    name_to_number = {s["Name"]: s["Id"] for s in students}
    return number_to_name, name_to_number

number_to_name, name_to_number = load_students()

# 시간표 데이터 불러오기
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

# 급식 API 설정
API_KEY = 'cc3aadcf25ef44c5bff79f95bc63b78a'
SCHOOL_CODE = '9300117'
OFFICE_CODE = 'I10'

# 급식 정보 요청 파싱 (Wit.ai entity 기반)
def parse_meal_request(entities):
    now = datetime.utcnow() + timedelta(hours=9)
    today = now.strftime('%Y-%m-%d')
    tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')

    meal_date_entity = entities.get("meal_date:meal_date", [{}])[0].get("value", None)
    meal_type = entities.get("meal_type:meal_type", [{}])[0].get("value", None)

    if meal_date_entity == "오늘":
        date = today
    elif meal_date_entity == "내일":
        date = tomorrow
    else:
        date = None

    print("날짜 파싱: ", date)
    print("식사 종류 파싱: ", meal_type)

    return date, meal_type


# 급식 데이터 불러오기
def get_lunch_info(date, meal_type):
    formatted_date = date.replace('-', '')
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE={OFFICE_CODE}&SD_SCHUL_CODE={SCHOOL_CODE}&MLSV_YMD={formatted_date}&KEY={API_KEY}&Type=json"

    try:
        res = requests.get(url)
        data = res.json()
        meals_info = data.get('mealServiceDietInfo')
        if not meals_info or len(meals_info) < 2:
            return '급식 정보가 없습니다.'

        meals = meals_info[1].get('row', [])
        if not meals:
            return '급식 정보가 없습니다.'

        if meal_type:
            meals = [m for m in meals if m.get('MMEAL_SC_NM') == meal_type]
            if not meals:
                return f"{meal_type} 정보가 없습니다."

        result = ''
        for meal in meals:
            name = meal.get('MMEAL_SC_NM')
            dish = meal.get('DDISH_NM', '').replace('<br/>', '\n')
            dish = re.sub(r'\([0-9.]+\)', '', dish)
            result += f"【{name}】\n{dish.strip()}\n\n"

        return result.strip()
    except Exception as e:
        print("급식 API 오류:", e)
        return '급식 정보를 불러오는 데 실패했습니다.'

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

# 질문 응답 처리 API
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("text", "")

    wit_data = get_wit_response(user_input)

    print("Wit.ai 전체 응답: ", json.dumps(wit_data, ensure_ascii=False, indent=2), flush=True)
    intent = wit_data.get("intents", [{}])[0].get("name", "")
    entities = wit_data.get("entities", {})

    
    print("🎯 인식된 intent:", intent, flush=True)
    print("📦 인식된 entities:", json.dumps(entities, ensure_ascii=False), flush=True)


    if intent == "get_teacher_name":
        answer = "우리 반 담임 선생님은 장세민 선생님이야!"

    elif intent == "get_student_name":
        number_entity = entities.get("student_number:student_number", [{}])[0].get("value")
        if number_entity:
            full_number = f"310{int(number_entity):02d}"
            student_name = number_to_name.get(full_number)
            if student_name:
                answer = f"{number_entity}번 학생은 {student_name}야!"
            else:
                answer = f"{number_entity}번? 그 번호를 가진 학생은 없는 것 같아!"
        else:
            answer = "몇 번인지 잘 못 들었어!"

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

    elif intent == "get_subject_by_time":
        weekday_entity = entities.get("weekday:weekday", [{}])[0].get("value")
        time_entity = entities.get("time:time", [{}])[0].get("value")

        if weekday_entity and time_entity:
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

    elif intent == "get_lunch_info":
        date, meal_type = parse_meal_request(entities)
        if date:
            answer = get_lunch_info(date, meal_type)
        else:
            answer = "오늘 / 내일, 중식 / 석식 중 언제 급식을 알고 싶은지 말해줘!"

    else:
        answer = "음... 질문을 잘 이해하지 못했어"

    return jsonify({"answer": answer})

# 실행 코드
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
