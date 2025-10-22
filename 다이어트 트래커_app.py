import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="주간 식단·걷기 트래커", page_icon="🥗", layout="wide")

# -----------------------------
# Utilities & Defaults
# -----------------------------
def init_state():
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "age": 52,
            "sex": "여성",
            "height_cm": 160,
            "weight_kg": 65.0,
            "activity_factor": 1.35,  # walking-focused, light-moderate
            "daily_calorie_goal": 1450,
            "weekend_20k_steps": True,
            "step_kcal_factor": 0.04, # kcal per step (adjustable)
            "fixed_breakfast": {
                "사과(1/2개)": 1.0,
                "삶은 달걀": 2.0,
                "무가당 요거트(1컵)": 1.0,
                "견과류 한 줌(약 20g)": 1.0,
            }
        }
    if "foods_df" not in st.session_state:
        st.session_state.foods_df = pd.DataFrame([
            {"이름":"현미밥(1/2공기)", "1회 제공량":1, "kcal":150, "단백질_g":3.5, "탄수화물_g":32, "지방_g":1.2},
            {"이름":"보리밥(1공기)", "1회 제공량":1, "kcal":320, "단백질_g":6.5, "탄수화물_g":68, "지방_g":1.2},
            {"이름":"닭가슴살(100g)", "1회 제공량":1, "kcal":165, "단백질_g":31, "탄수화물_g":0, "지방_g":3.6},
            {"이름":"두부(150g)", "1회 제공량":1, "kcal":120, "단백질_g":12, "탄수화물_g":3, "지방_g":7},
            {"이름":"연어구이(120g)", "1회 제공량":1, "kcal":235, "단백질_g":25, "탄수화물_g":0, "지방_g":14},
            {"이름":"오트밀(40g)", "1회 제공량":1, "kcal":150, "단백질_g":5, "탄수화물_g":27, "지방_g":3},
            {"이름":"고구마(100g)", "1회 제공량":1, "kcal":90, "단백질_g":1.5, "탄수화물_g":21, "지방_g":0.1},
            {"이름":"시금치나물(80g)", "1회 제공량":1, "kcal":50, "단백질_g":3, "탄수화물_g":5, "지방_g":1.5},
            {"이름":"브로콜리(100g)", "1회 제공량":1, "kcal":35, "단백질_g":3, "탄수화물_g":6, "지방_g":0.4},
            {"이름":"된장국(1그릇)", "1회 제공량":1, "kcal":60, "단백질_g":5, "탄수화물_g":5, "지방_g":2},
            {"이름":"미역국(1그릇)", "1회 제공량":1, "kcal":45, "단백질_g":3, "탄수화물_g":4, "지방_g":1},
            {"이름":"사과(1/2개)", "1회 제공량":1, "kcal":45, "단백질_g":0.2, "탄수화물_g":12, "지방_g":0.1},
            {"이름":"삶은 달걀", "1회 제공량":1, "kcal":77, "단백질_g":6.3, "탄수화물_g":0.6, "지방_g":5.3},
            {"이름":"무가당 요거트(1컵)", "1회 제공량":1, "kcal":95, "단백질_g":9, "탄수화물_g":7, "지방_g":3},
            {"이름":"견과류 한 줌(약 20g)", "1회 제공량":1, "kcal":120, "단백질_g":4, "탄수화물_g":4, "지방_g":10},
            {"이름":"아몬드 10알", "1회 제공량":1, "kcal":70, "단백질_g":2.6, "탄수화물_g":2.5, "지방_g":6},
            {"이름":"방울토마토 5개", "1회 제공량":1, "kcal":20, "단백질_g":1, "탄수화물_g":4, "지방_g":0.2},
            {"이름":"블루베리 10알", "1회 제공량":1, "kcal":15, "단백질_g":0.2, "탄수화물_g":3.5, "지방_g":0.1},
            {"이름":"제육볶음(120g, 저지방)", "1회 제공량":1, "kcal":250, "단백질_g":20, "탄수화물_g":8, "지방_g":14},
            {"이름":"고등어조림(120g)", "1회 제공량":1, "kcal":260, "단백질_g":22, "탄수화물_g":2, "지방_g":18},
            {"이름":"연두부(150g)", "1회 제공량":1, "kcal":90, "단백질_g":8, "탄수화물_g":3, "지방_g":5},
            {"이름":"닭가슴살샐러드(1접시)", "1회 제공량":1, "kcal":230, "단백질_g":28, "탄수화물_g":10, "지방_g":8},
        ])
    if "ex_df" not in st.session_state:
        st.session_state.ex_df = pd.DataFrame([
            {"운동":"걷기(보수 입력)", "단위":"걸음", "kcal_per_unit":st.session_state.profile["step_kcal_factor"]},
            {"운동":"계단 오르기", "단위":"분", "kcal_per_unit":8.0},
            {"운동":"요가(가벼움)", "단위":"분", "kcal_per_unit":3.0},
            {"운동":"근력(가벼움)", "단위":"분", "kcal_per_unit":5.0},
        ])
    if "planner" not in st.session_state:
        # 7-day meal planner (lunch/dinner/snack)
        days = ["월","화","수","목","금","토","일"]
        st.session_state.planner = pd.DataFrame({
            "요일": days,
            "점심": [
                "현미밥(1/2공기)+닭가슴살(100g)+시금치나물+된장국",
                "보리밥(1공기)+연어구이(120g)+단호박+미역무침",
                "현미밥(1/2공기)+제육볶음(저지방)+양배추",
                "닭가슴살샐러드+고구마(1/2)+삶은 달걀(1)",
                "콩나물밥+된장찌개+김치",
                "연두부+채소샐러드+현미밥(1/3공기)",
                "현미밥(1/2공기)+소고기채소볶음+미역국",
            ],
            "저녁": [
                "두부조림+브로콜리+미역국",
                "오트밀(40g)+삶은 달걀(1)+오이무침",
                "두부부침+미역국+배추김치",
                "잡곡밥+고등어조림+미역줄기볶음",
                "오이닭가슴살무침+현미밥(1/3공기)",
                "오트밀죽+삶은 달걀(1)",
                "닭가슴살샐러드+고구마(1/2개)",
            ],
            "간식": [
                "블랙커피/허브차",
                "방울토마토 5개",
                "아몬드 10알",
                "사과 1/4개",
                "무가당 요거트 1/2컵",
                "아몬드 8알",
                "블루베리 10알",
            ],
            "메모": [""]*7
        })

init_state()

# -----------------------------
# Helper functions
# -----------------------------
def mifflin_st_jeor_bmr(sex:str, weight_kg:float, height_cm:float, age:int):
    s = -161 if sex == "여성" else 5
    return 10*weight_kg + 6.25*height_cm - 5*age + s

def tdee_from_bmr(bmr:float, activity_factor:float):
    return bmr * activity_factor

def kcal_from_steps(steps:int, factor:float):
    return steps * factor

def parse_foods_from_text(plan_text:str):
    # Split by '+' to map to names, sum kcal by DB lookup
    items = [t.strip() for t in plan_text.split('+') if t.strip()]
    return items

def kcal_of_items(items, foods_df:pd.DataFrame):
    kcal = 0.0
    for it in items:
        # match by prefix
        row = foods_df[foods_df["이름"].str.contains(it.split('(')[0].strip(), na=False)]
        if not row.empty:
            kcal += float(row.iloc[0]["kcal"])
    return kcal

def totals_for_day(lunch_text, dinner_text, snack_text, fixed_breakfast:dict, foods_df):
    # breakfast
    b_kcal = 0.0
    for k, amt in fixed_breakfast.items():
        row = foods_df[foods_df["이름"]==k]
        if not row.empty:
            b_kcal += float(row.iloc[0]["kcal"]) * float(amt)
    # lunch/dinner/snack
    l_kcal = kcal_of_items(parse_foods_from_text(lunch_text), foods_df)
    d_kcal = kcal_of_items(parse_foods_from_text(dinner_text), foods_df)
    s_kcal = kcal_of_items(parse_foods_from_text(snack_text), foods_df)
    return b_kcal + l_kcal + d_kcal + s_kcal

def save_json():
    payload = {
        "profile": st.session_state.profile,
        "foods": st.session_state.foods_df.to_dict(orient="records"),
        "exercises": st.session_state.ex_df.to_dict(orient="records"),
        "planner": st.session_state.planner.to_dict(orient="records"),
        "logs": st.session_state.get("logs", {}),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

def load_json(file_bytes:bytes):
    data = json.loads(file_bytes.decode("utf-8"))
    st.session_state.profile = data.get("profile", st.session_state.profile)
    st.session_state.foods_df = pd.DataFrame(data.get("foods", [])) or st.session_state.foods_df
    st.session_state.ex_df = pd.DataFrame(data.get("exercises", [])) or st.session_state.ex_df
    st.session_state.planner = pd.DataFrame(data.get("planner", [])) or st.session_state.planner
    st.session_state.logs = data.get("logs", {})

# -----------------------------
# Sidebar: Profile & Targets
# -----------------------------
st.sidebar.header("👤 프로필 & 목표")
age = st.sidebar.number_input("나이", 18, 90, value=int(st.session_state.profile["age"]))
sex = st.sidebar.selectbox("성별", ["여성","남성"], index=0 if st.session_state.profile["sex"]=="여성" else 1)
height = st.sidebar.number_input("키 (cm)", 120, 200, value=int(st.session_state.profile["height_cm"]))
weight = st.sidebar.number_input("현재 체중 (kg)", 35.0, 150.0, value=float(st.session_state.profile["weight_kg"]), step=0.1, format="%.1f")
act = st.sidebar.slider("활동계수 (걷기 중심)", 1.2, 1.7, value=float(st.session_state.profile["activity_factor"]), step=0.05)
step_factor = st.sidebar.slider("걸음당 소모 칼로리 (kcal/보)", 0.02, 0.07, value=float(st.session_state.profile["step_kcal_factor"]), step=0.005)
weekend20k = st.sidebar.checkbox("주말(토·일) 2만보", value=bool(st.session_state.profile["weekend_20k_steps"]))
daily_goal = st.sidebar.number_input("하루 섭취 칼로리 목표", 1100, 2200, value=int(st.session_state.profile["daily_calorie_goal"]), step=50)

st.session_state.profile.update({
    "age": age, "sex": sex, "height_cm": height, "weight_kg": weight,
    "activity_factor": act, "step_kcal_factor": step_factor,
    "weekend_20k_steps": weekend20k, "daily_calorie_goal": daily_goal
})

bmr = mifflin_st_jeor_bmr(sex, weight, height, age)
tdee = tdee_from_bmr(bmr, act)
st.sidebar.markdown(f"**BMR:** {bmr:.0f} kcal / **TDEE:** {tdee:.0f} kcal")

with st.sidebar.expander("🍽️ 아침(고정) 구성 확인/수정"):
    bf = st.session_state.profile["fixed_breakfast"]
    for k in list(bf.keys()):
        amt = st.number_input(f"{k} (개수/회)", min_value=0.0, max_value=5.0, value=float(bf[k]), step=0.5, key=f"bf_{k}")
        bf[k] = amt
    st.caption("※ 0으로 두면 해당 항목은 제외됩니다.")

st.sidebar.divider()
st.sidebar.subheader("💾 저장 / 불러오기")
colA, colB = st.sidebar.columns(2)
with colA:
    st.download_button("데이터 내보내기(JSON)", data=save_json(), file_name="diet_walking_tracker.json", mime="application/json")
with colB:
    up = st.file_uploader("불러오기(JSON)", type=["json"], label_visibility="collapsed")
    if up is not None:
        load_json(up.read())
        st.success("불러오기 완료!")

# -----------------------------
# Main Tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📅 주간 계획", "📝 일일 기록", "🍲 음식/운동 DB", "📈 진행 상황"])

# --- Tab1: Weekly Planner ---
with tab1:
    st.markdown("### 📅 주간 식단 계획 (점심/저녁/간식 편집 가능)")
    st.caption("아침은 고정 구성을 사용합니다. 각 칸은 '+'로 음식을 연결합니다. (예: '현미밥(1/2공기)+닭가슴살(100g)')")

    st.session_state.planner = st.data_editor(
        st.session_state.planner,
        num_rows="fixed",
        use_container_width=True,
        key="planner_editor"
    )

    # Show estimated kcal per day based on DB
    st.markdown("#### 🔢 일일 예상 섭취 칼로리(아침 포함)")
    rows = []
    for _, r in st.session_state.planner.iterrows():
        tot = totals_for_day(r["점심"], r["저녁"], r["간식"], st.session_state.profile["fixed_breakfast"], st.session_state.foods_df)
        rows.append({"요일": r["요일"], "예상 섭취 kcal": round(tot)})
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    st.info("TIP: 음식 DB에 없는 항목은 먼저 '🍲 음식/운동 DB' 탭에서 추가한 뒤, 여기에 이름을 입력하세요.")

# --- Tab2: Daily Log ---
with tab2:
    st.markdown("### 📝 일일 기록 & 목표 달성 체크")
    today = st.date_input("기록 날짜", value=datetime.now().date())
    key_day = today.isoformat()
    if "logs" not in st.session_state:
        st.session_state.logs = {}
    logs = st.session_state.logs.get(key_day, {
        "breakfast_override": {},  # name->count
        "meals": [],               # list of (이름, 수량)
        "custom_kcal": 0,          # manual adjustments
        "steps": 8000,
        "exercises": [],           # list of (운동, 수량)
        "note": "",
        "goal_done": False,
    })

    st.subheader("🍽️ 섭취")
    st.caption("기본은 고정 아침식이 적용됩니다. 필요하면 수량을 조정하세요.")
    with st.expander("아침 대체/가감 입력"):
        bf_edits = {}
        for name in st.session_state.profile["fixed_breakfast"].keys():
            amt = st.number_input(f"{name}", 0.0, 5.0, value=float(st.session_state.profile["fixed_breakfast"][name]), step=0.5, key=f"log_bf_{name}")
            if amt > 0:
                bf_edits[name] = amt
        logs["breakfast_override"] = bf_edits

    foods = st.session_state.foods_df["이름"].tolist()
    with st.expander("점심/저녁/간식 추가", expanded=True):
        add_food = st.selectbox("음식 선택", ["- 선택 -"] + foods, index=0, key="sel_food")
        qty = st.number_input("수량 (회)", 0.0, 10.0, 1.0, 0.5)
        if st.button("추가", use_container_width=True):
            if add_food != "- 선택 -":
                logs["meals"].append((add_food, float(qty)))

        if logs["meals"]:
            df_meal = pd.DataFrame(logs["meals"], columns=["이름","수량(회)"])
            st.dataframe(df_meal, use_container_width=True)
            idx_del = st.number_input("삭제할 행 번호(위 표의 인덱스)", -1, len(df_meal)-1, -1)
            if st.button("선택 행 삭제"):
                if idx_del >= 0:
                    del logs["meals"][idx_del]

    st.subheader("🔥 소비")
    steps = st.number_input("오늘 걸음 수", 0, 100000, value=int(logs.get("steps", 8000)), step=500)
    logs["steps"] = steps
    ex_list = st.session_state.ex_df["운동"].tolist()
    with st.expander("운동 추가", expanded=False):
        ex = st.selectbox("운동 선택", ["- 선택 -"] + ex_list, index=0)
        amount = st.number_input("수량(단위: 분 또는 걸음)", 0.0, 100000.0, 20.0, 5.0)
        if st.button("운동 추가", use_container_width=True):
            if ex != "- 선택 -":
                logs["exercises"].append((ex, float(amount)))
        if logs["exercises"]:
            df_ex = pd.DataFrame(logs["exercises"], columns=["운동","수량"])
            st.dataframe(df_ex, use_container_width=True)
            i2 = st.number_input("삭제할 운동 행 번호", -1, len(df_ex)-1, -1, key="del_ex_idx")
            if st.button("선택 운동 삭제"):
                if i2 >= 0:
                    del logs["exercises"][i2]

    st.subheader("🧮 칼로리 계산")
    foods_df = st.session_state.foods_df.set_index("이름")
    # Breakfast kcal
    def kcal_of(name):
        return float(foods_df.loc[name]["kcal"]) if name in foods_df.index else 0.0

    bf_kcal = 0.0
    for name, amt in logs["breakfast_override"].items():
        bf_kcal += kcal_of(name) * amt

    meal_kcal = 0.0
    for name, qty in logs["meals"]:
        meal_kcal += kcal_of(name) * qty

    intake = bf_kcal + meal_kcal + float(logs.get("custom_kcal", 0.0))
    steps_kcal = st.session_state.profile["step_kcal_factor"] * steps

    # exercise kcal
    ex_kcal = 0.0
    for (ename, qty) in logs["exercises"]:
        row = st.session_state.ex_df[st.session_state.ex_df["운동"]==ename]
        if not row.empty:
            ex_kcal += float(row.iloc[0]["kcal_per_unit"]) * float(qty)

    burn = steps_kcal + ex_kcal

    st.metric("섭취 칼로리", f"{int(intake)} kcal")
    st.metric("소비 칼로리", f"{int(burn)} kcal")
    st.metric("칼로리 밸런스(섭취-소비)", f"{int(intake - burn)} kcal")

    st.subheader("✅ 목표 달성 체크")
    goal = intake <= st.session_state.profile["daily_calorie_goal"]
    done = st.checkbox("오늘 목표 달성", value=bool(logs.get("goal_done", goal)))
    logs["goal_done"] = done
    note = st.text_area("메모", value=logs.get("note",""))
    logs["note"] = note

    # Save logs for day
    st.session_state.logs[key_day] = logs
    st.success("해당 날짜 기록이 임시 저장되었습니다. (브라우저/세션 기준)")

    # Export logs
    if st.button("모든 기록 CSV로 내보내기"):
        rows = []
        for day, lg in st.session_state.logs.items():
            rows.append({
                "날짜": day,
                "섭취_kcal": round(intake if day==key_day else np.nan, 2),
                "소비_kcal": round(burn if day==key_day else np.nan, 2),
                "목표달성": lg.get("goal_done", False),
                "걸음수": lg.get("steps", 0),
                "메모": lg.get("note","")
            })
        csv = pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig")
        st.download_button("CSV 다운로드", data=csv, file_name="logs.csv", mime="text/csv")

# --- Tab3: Databases ---
with tab3:
    st.markdown("### 🍲 음식 DB (칼로리/영양)")
    st.caption("식단에 활용할 음식과 1회 제공량 당 칼로리를 관리합니다.")
    st.session_state.foods_df = st.data_editor(st.session_state.foods_df, num_rows="dynamic", use_container_width=True, key="food_editor")
    st.markdown("### 🏃 운동 DB")
    st.caption("운동별 소모 칼로리(단위 당)를 관리합니다. 걷기는 걸음당 칼로리로 계산됩니다.")
    st.session_state.ex_df = st.data_editor(st.session_state.ex_df, num_rows="dynamic", use_container_width=True, key="ex_editor")

# --- Tab4: Progress ---
with tab4:
    st.markdown("### 📈 주간/월간 진행 상황 요약")
    if st.session_state.get("logs"):
        df_rows = []
        for day, lg in st.session_state.logs.items():
            # Recompute each day based on saved snapshot if needed (simplified)
            # Here we store only steps & goal flag; intake/burn are recomputed for the active day; others left blank.
            df_rows.append({"날짜": day, "걸음수": lg.get("steps",0), "목표달성": lg.get("goal_done", False)})
        dfp = pd.DataFrame(df_rows).sort_values("날짜")
        st.dataframe(dfp, use_container_width=True)
        streak = dfp["목표달성"].astype(bool).astype(int).rolling(window=7).sum().max()
        st.metric("최근 7일 목표 달성 최대 연속일", int(streak if pd.notna(streak) else 0))
    else:
        st.info("아직 기록이 없습니다. '📝 일일 기록' 탭에서 오늘부터 시작해 보세요!")

st.caption("※ 건강 관련 수치는 일반적인 참고용입니다. 당뇨 등 질환이 의심되면 반드시 의료진과 상담하세요.")
