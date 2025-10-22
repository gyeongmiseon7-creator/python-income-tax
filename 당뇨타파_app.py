import streamlit as st
import pandas as pd
import numpy as np
import json, os, time, base64, io, requests
from datetime import datetime, date
from collections import defaultdict

st.set_page_config(page_title="주간 식단·걷기 트래커", page_icon="🥗", layout="wide")

# =============================
# Utilities & Defaults
# =============================
def init_state():
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "age": 52,
            "sex": "여성",
            "height_cm": 160,
            "weight_kg": 65.0,
            "activity_factor": 1.35,  # walking-focused
            "daily_calorie_goal": 1450,
            "weekend_20k_steps": True,
            "step_kcal_factor": 0.04,  # kcal per step
            "fixed_breakfast": {
                "사과(1/2개)": 1.0,
                "삶은 달걀": 2.0,
                "무가당 요거트(1컵)": 1.0,
                "견과류 한 줌(약 20g)": 1.0,
            },
        }

    if "foods_df" not in st.session_state:
        # Expanded foods DB with fiber column (g). Values are approximate per serving.
        st.session_state.foods_df = pd.DataFrame([
            {"이름":"현미밥(1/2공기)", "1회 제공량":1, "kcal":150, "단백질_g":3.5, "탄수화물_g":32, "지방_g":1.2, "식이섬유_g":1.8},
            {"이름":"현미밥(1공기)", "1회 제공량":1, "kcal":300, "단백질_g":7, "탄수화물_g":64, "지방_g":2.4, "식이섬유_g":3.6},
            {"이름":"잡곡밥(1공기)", "1회 제공량":1, "kcal":320, "단백질_g":7, "탄수화물_g":68, "지방_g":2.0, "식이섬유_g":4.0},
            {"이름":"보리밥(1공기)", "1회 제공량":1, "kcal":320, "단백질_g":6.5, "탄수화물_g":68, "지방_g":1.2, "식이섬유_g":4.5},
            {"이름":"귀리밥(1공기)", "1회 제공량":1, "kcal":330, "단백질_g":9, "탄수화물_g":62, "지방_g":4, "식이섬유_g":5.0},
            {"이름":"오트밀(40g)", "1회 제공량":1, "kcal":150, "단백질_g":5, "탄수화물_g":27, "지방_g":3, "식이섬유_g":4.0},
            {"이름":"퀴노아(1/2공기)", "1회 제공량":1, "kcal":110, "단백질_g":4, "탄수화물_g":19, "지방_g":2, "식이섬유_g":2.0},
            {"이름":"고구마(100g)", "1회 제공량":1, "kcal":90, "단백질_g":1.5, "탄수화물_g":21, "지방_g":0.1, "식이섬유_g":3.0},
            {"이름":"단호박(100g)", "1회 제공량":1, "kcal":70, "단백질_g":1.8, "탄수화물_g":16, "지방_g":0.2, "식이섬유_g":1.5},
            {"이름":"통밀빵(1장)", "1회 제공량":1, "kcal":90, "단백질_g":4, "탄수화물_g":16, "지방_g":1.2, "식이섬유_g":2.0},
            {"이름":"메밀소바(1인분)", "1회 제공량":1, "kcal":280, "단백질_g":12, "탄수화물_g":54, "지방_g":2, "식이섬유_g":3.0},
            {"이름":"닭가슴살(100g)", "1회 제공량":1, "kcal":165, "단백질_g":31, "탄수화물_g":0, "지방_g":3.6, "식이섬유_g":0},
            {"이름":"훈제 닭가슴살(100g)", "1회 제공량":1, "kcal":130, "단백질_g":24, "탄수화물_g":3, "지방_g":2, "식이섬유_g":0},
            {"이름":"소고기 우둔(100g)", "1회 제공량":1, "kcal":180, "단백질_g":24, "탄수화물_g":0, "지방_g":9, "식이섬유_g":0},
            {"이름":"돼지 안심(100g)", "1회 제공량":1, "kcal":170, "단백질_g":22, "탄수화물_g":0, "지방_g":8, "식이섬유_g":0},
            {"이름":"제육볶음(120g, 저지방)", "1회 제공량":1, "kcal":250, "단백질_g":20, "탄수화물_g":8, "지방_g":14, "식이섬유_g":1.0},
            {"이름":"연어구이(120g)", "1회 제공량":1, "kcal":235, "단백질_g":25, "탄수화물_g":0, "지방_g":14, "식이섬유_g":0},
            {"이름":"고등어조림(120g)", "1회 제공량":1, "kcal":260, "단백질_g":22, "탄수화물_g":2, "지방_g":18, "식이섬유_g":0},
            {"이름":"참치캔(물)+(100g)", "1회 제공량":1, "kcal":120, "단백질_g":26, "탄수화물_g":0, "지방_g":1, "식이섬유_g":0},
            {"이름":"두부(150g)", "1회 제공량":1, "kcal":120, "단백질_g":12, "탄수화물_g":3, "지방_g":7, "식이섬유_g":1.5},
            {"이름":"연두부(150g)", "1회 제공량":1, "kcal":90, "단백질_g":8, "탄수화물_g":3, "지방_g":5, "식이섬유_g":1.0},
            {"이름":"달걀프라이", "1회 제공량":1, "kcal":90, "단백질_g":6, "탄수화물_g":0.4, "지방_g":7, "식이섬유_g":0},
            {"이름":"삶은 달걀", "1회 제공량":1, "kcal":77, "단백질_g":6.3, "탄수화물_g":0.6, "지방_g":5.3, "식이섬유_g":0},
            {"이름":"콩(삶은, 100g)", "1회 제공량":1, "kcal":140, "단백질_g":12, "탄수화물_g":10, "지방_g":6, "식이섬유_g":5.0},
            {"이름":"된장국(1그릇)", "1회 제공량":1, "kcal":60, "단백질_g":5, "탄수화물_g":5, "지방_g":2, "식이섬유_g":1.0},
            {"이름":"미역국(1그릇)", "1회 제공량":1, "kcal":45, "단백질_g":3, "탄수화물_g":4, "지방_g":1, "식이섬유_g":0.8},
            {"이름":"김치찌개(1그릇)", "1회 제공량":1, "kcal":180, "단백질_g":12, "탄수화물_g":6, "지방_g":10, "식이섬유_g":1.5},
            {"이름":"순두부찌개(1그릇)", "1회 제공량":1, "kcal":220, "단백질_g":16, "탄수화물_g":8, "지방_g":12, "식이섬유_g":1.5},
            {"이름":"시금치나물(80g)", "1회 제공량":1, "kcal":50, "단백질_g":3, "탄수화물_g":5, "지방_g":1.5, "식이섬유_g":2.5},
            {"이름":"콩나물무침(80g)", "1회 제공량":1, "kcal":60, "단백질_g":4, "탄수화물_g":6, "지방_g":2, "식이섬유_g":2.0},
            {"이름":"브로콜리(100g)", "1회 제공량":1, "kcal":35, "단백질_g":3, "탄수화물_g":6, "지방_g":0.4, "식이섬유_g":2.6},
            {"이름":"양배추쌈(80g)", "1회 제공량":1, "kcal":25, "단백질_g":1.5, "탄수화물_g":5, "지방_g":0.2, "식이섬유_g":1.8},
            {"이름":"오이무침(80g)", "1회 제공량":1, "kcal":35, "단백질_g":1, "탄수화물_g":6, "지방_g":0.2, "식이섬유_g":0.8},
            {"이름":"미역줄기볶음(80g)", "1회 제공량":1, "kcal":70, "단백질_g":2, "탄수화물_g":8, "지방_g":3, "식이섬유_g":1.5},
            {"이름":"샐러드 채소(1접시)", "1회 제공량":1, "kcal":40, "단백질_g":2, "탄수화물_g":7, "지방_g":0.5, "식이섬유_g":3.0},
            {"이름":"무가당 요거트(1컵)", "1회 제공량":1, "kcal":95, "단백질_g":9, "탄수화물_g":7, "지방_g":3, "식이섬유_g":0},
            {"이름":"저지방 우유(200ml)", "1회 제공량":1, "kcal":95, "단백질_g":7, "탄수화물_g":10, "지방_g":3, "식이섬유_g":0},
            {"이름":"코티지치즈(50g)", "1회 제공량":1, "kcal":80, "단백질_g":10, "탄수화물_g":3, "지방_g":3, "식이섬유_g":0},
            {"이름":"사과(1/2개)", "1회 제공량":1, "kcal":45, "단백질_g":0.2, "탄수화물_g":12, "지방_g":0.1, "식이섬유_g":2.0},
            {"이름":"바나나(소1개)", "1회 제공량":1, "kcal":90, "단백질_g":1.1, "탄수화물_g":23, "지방_g":0.3, "식이섬유_g":2.6},
            {"이름":"블루베리 10알", "1회 제공량":1, "kcal":15, "단백질_g":0.2, "탄수화물_g":3.5, "지방_g":0.1, "식이섬유_g":0.6},
            {"이름":"딸기(5개)", "1회 제공량":1, "kcal":20, "단백질_g":0.4, "탄수화물_g":4.8, "지방_g":0.2, "식이섬유_g":1.0},
            {"이름":"아몬드 10알", "1회 제공량":1, "kcal":70, "단백질_g":2.6, "탄수화물_g":2.5, "지방_g":6, "식이섬유_g":1.7},
            {"이름":"호두(4쪽)", "1회 제공량":1, "kcal":100, "단백질_g":2, "탄수화물_g":2, "지방_g":10, "식이섬유_g":1.0},
            {"이름":"땅콩(20g)", "1회 제공량":1, "kcal":120, "단백질_g":5, "탄수화물_g":4, "지방_g":10, "식이섬유_g":1.2},
            {"이름":"고구마말랭이(20g)", "1회 제공량":1, "kcal":70, "단백질_g":0.5, "탄수화물_g":17, "지방_g":0.1, "식이섬유_g":1.5},
            {"이름":"배추김치(50g)", "1회 제공량":1, "kcal":12, "단백질_g":1, "탄수화물_g":2, "지방_g":0.2, "식이섬유_g":1.1},
            {"이름":"김(3장)", "1회 제공량":1, "kcal":15, "단백질_g":1.5, "탄수화물_g":1, "지방_g":0.3, "식이섬유_g":0.5},
            {"이름":"닭가슴살샐러드(1접시)", "1회 제공량":1, "kcal":230, "단백질_g":28, "탄수화물_g":10, "지방_g":8, "식이섬유_g":3.0},
            {"이름":"소고기채소볶음(1접시)", "1회 제공량":1, "kcal":280, "단백질_g":22, "탄수화물_g":12, "지방_g":14, "식이섬유_g":2.5},
            {"이름":"오이닭가슴살무침(1접시)", "1회 제공량":1, "kcal":210, "단백질_g":26, "탄수화물_g":8, "지방_g":8, "식이섬유_g":2.0},
            {"이름":"오트밀죽(1그릇)", "1회 제공량":1, "kcal":220, "단백질_g":9, "탄수화물_g":35, "지방_g":4, "식이섬유_g":4.0},
            {"이름":"잡곡밥(1/3공기)", "1회 제공량":1, "kcal":210, "단백질_g":4.5, "탄수화물_g":45, "지방_g":1.2, "식이섬유_g":2.5},
        ])

    # Ensure fiber column exists even if user loads old JSON
    if "식이섬유_g" not in st.session_state.foods_df.columns:
        st.session_state.foods_df["식이섬유_g"] = 0.0

    if "ex_df" not in st.session_state:
        st.session_state.ex_df = pd.DataFrame([
            {"운동":"걷기(보수 입력)", "단위":"걸음", "kcal_per_unit":st.session_state.profile["step_kcal_factor"]},
            {"운동":"빠른 걷기", "단위":"분", "kcal_per_unit":5.5},
            {"운동":"실내걷기", "단위":"분", "kcal_per_unit":4.0},
            {"운동":"조깅(가볍게)", "단위":"분", "kcal_per_unit":8.0},
            {"운동":"계단 오르기", "단위":"분", "kcal_per_unit":8.0},
            {"운동":"실내 자전거(가볍게)", "단위":"분", "kcal_per_unit":6.0},
            {"운동":"사이클(중간)", "단위":"분", "kcal_per_unit":8.0},
            {"운동":"수영(천천히)", "단위":"분", "kcal_per_unit":7.0},
            {"운동":"요가(가벼움)", "단위":"분", "kcal_per_unit":3.0},
            {"운동":"필라테스", "단위":"분", "kcal_per_unit":4.5},
            {"운동":"근력(가벼움)", "단위":"분", "kcal_per_unit":5.0},
            {"운동":"근력(중간)", "단위":"분", "kcal_per_unit":7.0},
            {"운동":"줄넘기(천천히)", "단위":"분", "kcal_per_unit":9.0},
            {"운동":"등산(완만)", "단위":"분", "kcal_per_unit":8.0},
            {"운동":"스트레칭", "단위":"분", "kcal_per_unit":2.0},
            {"운동":"청소/정리", "단위":"분", "kcal_per_unit":3.0},
            {"운동":"자세교정/재활", "단위":"분", "kcal_per_unit":2.5},
            {"운동":"런지/스쿼트", "단위":"분", "kcal_per_unit":6.0},
            {"운동":"훌라후프", "단위":"분", "kcal_per_unit":4.0},
        ])

    if "planner" not in st.session_state:
        days = ["월","화","수","목","금","토","일"]
        st.session_state.planner = pd.DataFrame({
            "요일": days,
            "점심": [
                "현미밥(1/2공기)+닭가슴살(100g)+시금치나물+된장국",
                "보리밥(1공기)+연어구이(120g)+단호박+미역무침",
                "현미밥(1/2공기)+제육볶음(저지방)+양배추쌈",
                "닭가슴살샐러드+고구마(1/2)+삶은 달걀(1)",
                "콩나물밥+된장찌개+김치",
                "연두부+샐러드 채소+현미밥(1/3공기)",
                "현미밥(1/2공기)+소고기채소볶음+미역국",
            ],
            "저녁": [
                "두부조림+브로콜리+미역국",
                "오트밀(40g)+삶은 달걀(1)+오이무침",
                "두부부침+미역국+배추김치",
                "잡곡밥(1/3공기)+고등어조림+미역줄기볶음",
                "오이닭가슴살무침+현미밥(1/3공기)",
                "오트밀죽(1그릇)+삶은 달걀(1)",
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
            "메모": [""]*7,
        })

    if "logs" not in st.session_state:
        st.session_state.logs = {}

    if "vision_cfg" not in st.session_state:
        st.session_state.vision_cfg = {
            "provider": "수동/웹훅",
            "api_key": "",
            "endpoint": "",
        }

init_state()

# =============================
# Helper functions
# =============================
def mifflin_st_jeor_bmr(sex:str, weight_kg:float, height_cm:float, age:int):
    s = -161 if sex == "여성" else 5
    return 10*weight_kg + 6.25*height_cm - 5*age + s

def tdee_from_bmr(bmr:float, activity_factor:float):
    return bmr * activity_factor

def weekday_kr(d:date):
    return "월화수목금토일"[d.weekday()]

def save_json():
    payload = {
        "profile": st.session_state.profile,
        "foods": st.session_state.foods_df.to_dict(orient="records"),
        "exercises": st.session_state.ex_df.to_dict(orient="records"),
        "planner": st.session_state.planner.to_dict(orient="records"),
        "logs": st.session_state.logs,
        "vision_cfg": st.session_state.vision_cfg,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

def load_json(file_bytes:bytes):
    data = json.loads(file_bytes.decode("utf-8"))
    st.session_state.profile = data.get("profile", st.session_state.profile)
    st.session_state.foods_df = pd.DataFrame(data.get("foods", [])) or st.session_state.foods_df
    if "식이섬유_g" not in st.session_state.foods_df.columns:
        st.session_state.foods_df["식이섬유_g"] = 0.0
    st.session_state.ex_df = pd.DataFrame(data.get("exercises", [])) or st.session_state.ex_df
    st.session_state.planner = pd.DataFrame(data.get("planner", [])) or st.session_state.planner
    st.session_state.logs = data.get("logs", {})
    st.session_state.vision_cfg = data.get("vision_cfg", st.session_state.vision_cfg)

def kcal_of(name, foods_df):
    return float(foods_df.loc[name]["kcal"]) if name in foods_df.index else 0.0

def macros_of(name, foods_df):
    if name in foods_df.index:
        r = foods_df.loc[name]
        return float(r["단백질_g"]), float(r["탄수화물_g"]), float(r["지방_g"]), float(r.get("식이섬유_g",0.0))
    return 0.0,0.0,0.0,0.0

def diet_quality_score(total_kcal, protein_g, carb_g, fat_g, fiber_g):
    if total_kcal <= 0:
        return 0
    # Percent of kcal from macros
    p_pct = (protein_g*4)/total_kcal
    c_pct = (carb_g*4)/total_kcal
    f_pct = (fat_g*9)/total_kcal
    # Components (simple heuristic):
    score = 0
    # Protein target 20~30%
    if 0.20 <= p_pct <= 0.30: score += 35
    elif 0.15 <= p_pct <= 0.35: score += 25
    # Fiber per 1000 kcal: ≥12g ideal, ≥8g okay
    fiber_per_1000 = fiber_g / max(total_kcal/1000.0, 1e-6)
    if fiber_per_1000 >= 12: score += 35
    elif fiber_per_1000 >= 8: score += 25
    # Carb balance 35~50% (lower GI 가정): generous range
    if 0.35 <= c_pct <= 0.50: score += 20
    elif 0.30 <= c_pct <= 0.55: score += 10
    # Fat cap ≤35%
    if f_pct <= 0.35: score += 10
    return int(min(score, 100))

def analyze_image_with_webhook(image_bytes:bytes, endpoint:str, api_key:str=""):
    """Generic webhook: POST {image: base64} -> {'items':[{'name':..., 'qty':1.0, 'confidence':0.9}, ...]}"""
    try:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        headers = {"Content-Type":"application/json"}
        if api_key: headers["Authorization"] = f"Bearer {api_key}"
        resp = requests.post(endpoint, json={"image": b64}, headers=headers, timeout=20)
        if resp.ok:
            return resp.json().get("items", [])
        else:
            return []
    except Exception:
        return []

# =============================
# Sidebar
# =============================
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

with st.sidebar.expander("🤖 사진 인식 설정"):
    prov = st.selectbox("프로바이더", ["수동/웹훅"], index=0)
    st.session_state.vision_cfg["provider"] = prov
    st.caption("웹훅 엔드포인트: POST JSON { image: base64 } → { items:[{name, qty, confidence}] }")
    st.session_state.vision_cfg["endpoint"] = st.text_input("웹훅 엔드포인트 URL", value=st.session_state.vision_cfg.get("endpoint",""))
    st.session_state.vision_cfg["api_key"] = st.text_input("API Key (선택)", value=st.session_state.vision_cfg.get("api_key",""), type="password")

st.sidebar.divider()
st.sidebar.subheader("💾 저장 / 불러오기")
c1, c2 = st.sidebar.columns(2)
with c1:
    st.download_button("데이터 내보내기(JSON)", data=save_json(), file_name="diet_walking_tracker.json", mime="application/json")
with c2:
    up = st.file_uploader("불러오기(JSON)", type=["json"], label_visibility="collapsed")
    if up is not None:
        load_json(up.read())
        st.success("불러오기 완료!")

# =============================
# Tabs
# =============================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 주간 계획", "📝 일일 기록", "🍲 음식/운동 DB", "📈 진행 상황", "🖼️ 앨범/타임라인"])

# --- Tab1 ---
with tab1:
    st.markdown("### 📅 주간 식단 계획 (점심/저녁/간식 편집 가능)")
    st.caption("아침은 고정. 각 칸은 '+'로 음식을 연결 (예: '현미밥(1/2공기)+닭가슴살(100g)').")

    st.session_state.planner = st.data_editor(
        st.session_state.planner,
        num_rows="fixed",
        use_container_width=True,
        key="planner_editor"
    )

    # Estimated kcal per day
    st.markdown("#### 🔢 일일 예상 섭취 칼로리(아침 포함)")
    rows = []
    for _, r in st.session_state.planner.iterrows():
        def kcal_lookup(text):
            items = [t.strip() for t in text.split('+') if t.strip()]
            kcal = 0.0
            for it in items:
                key = it.split('(')[0].strip()
                row = st.session_state.foods_df[st.session_state.foods_df["이름"].str.contains(f"^{key}", regex=True, na=False)]
                if not row.empty:
                    kcal += float(row.iloc[0]["kcal"])
            return kcal
        b_kcal = 0.0
        for k, amt in st.session_state.profile["fixed_breakfast"].items():
            row = st.session_state.foods_df[st.session_state.foods_df["이름"]==k]
            if not row.empty:
                b_kcal += float(row.iloc[0]["kcal"]) * float(amt)
        tot = b_kcal + kcal_lookup(r["점심"]) + kcal_lookup(r["저녁"]) + kcal_lookup(r["간식"])
        rows.append({"요일": r["요일"], "예상 섭취 kcal": round(tot)})
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
    st.info("DB에 없는 음식은 '🍲 음식/운동 DB' 탭에서 추가 후 사용하세요.")

# --- Tab2 ---
with tab2:
    st.markdown("### 📝 일일 기록 & 목표 달성 체크 (점심/저녁/간식 구분 + 사진 연동)")
    today = st.date_input("기록 날짜", value=datetime.now().date())
    st.caption(f"선택 날짜: {today.strftime('%Y-%m-%d')} ( {weekday_kr(today)} )")
    key_day = today.isoformat()
    logs = st.session_state.logs.get(key_day, {
        "breakfast_override": {},   # name->count
        "lunch": [], "dinner": [], "snacks": [],
        "steps": 8000,
        "exercises": [],
        "photos": [],   # {"file": path, "meal": "lunch/dinner/snacks", "items":[(name,qty)], "preview_kcal": float}
        "note": "",
        "goal_done": False,
    })

    # ------ Intake ------
    st.subheader("🍽️ 섭취")
    with st.expander("아침 대체/가감 입력"):
        bf_edits = {}
        for name in st.session_state.profile["fixed_breakfast"].keys():
            amt = st.number_input(f"{name}", 0.0, 5.0,
                                  value=float(st.session_state.profile["fixed_breakfast"][name]),
                                  step=0.5, key=f"log_bf_{name}")
            if amt > 0:
                bf_edits[name] = amt
        logs["breakfast_override"] = bf_edits

    foods = st.session_state.foods_df["이름"].tolist()

    def section_meal_editor(title, key_list_name):
        st.markdown(f"**{title} 추가**")
        colA, colB, colC = st.columns([3,1,1])
        with colA:
            sel = st.selectbox("음식 선택", ["- 선택 -"] + foods, index=0, key=f"sel_{key_list_name}")
        with colB:
            qty = st.number_input("수량(회)", 0.0, 10.0, 1.0, 0.5, key=f"qty_{key_list_name}")
        with colC:
            if st.button("추가", key=f"add_{key_list_name}", use_container_width=True):
                if sel != "- 선택 -":
                    logs[key_list_name].append((sel, float(qty)))

        if logs[key_list_name]:
            dfv = pd.DataFrame(logs[key_list_name], columns=["이름","수량(회)"])
            st.dataframe(dfv, use_container_width=True)
            idx = st.number_input("삭제할 행 번호", -1, len(dfv)-1, -1, key=f"del_idx_{key_list_name}")
            if st.button("선택 행 삭제", key=f"del_{key_list_name}"):
                if idx >= 0:
                    del logs[key_list_name][idx]

    with st.expander("점심", expanded=True):
        section_meal_editor("점심", "lunch")
    with st.expander("저녁", expanded=True):
        section_meal_editor("저녁", "dinner")
    with st.expander("간식", expanded=False):
        section_meal_editor("간식", "snacks")

    # ------ Photo to meal (with webhook) ------
    foods_df_idx = st.session_state.foods_df.set_index("이름")
    st.subheader("🖼️ 사진 업로드 → 식단 연동 + kcal 미리보기")
    upls = st.file_uploader("식사 사진 업로드 (jpg/png)", type=["jpg","jpeg","png"], accept_multiple_files=True)
    if upls:
        os.makedirs("uploads", exist_ok=True)
        for i, f in enumerate(upls):
            fname = f"{int(time.time())}_{i}_{f.name}"
            path = os.path.join("uploads", fname)
            with open(path, "wb") as out:
                out.write(f.getbuffer())
            st.image(path, caption=f"업로드됨: {fname}", use_column_width=True)

            # Optional: call webhook
            detected = []
            if st.session_state.vision_cfg.get("endpoint"):
                items = analyze_image_with_webhook(f.getvalue(), st.session_state.vision_cfg["endpoint"], st.session_state.vision_cfg.get("api_key",""))
                for it in items:
                    # Map names to DB entries if possible
                    name = it.get("name","")
                    qty = float(it.get("qty",1.0))
                    conf = float(it.get("confidence",0.0))
                    # best match by startswith
                    matches = [n for n in foods if n.startswith(name)]
                    if matches:
                        detected.append((matches[0], qty, conf))
                    elif name in foods:
                        detected.append((name, qty, conf))

            st.write("인식 결과(선택/수정 가능):")
            chosen = {}
            # Pre-fill with detected or empty selection UI
            det_names = [d[0] for d in detected] if detected else []
            sel_foods = st.multiselect("음식 선택(복수)", foods, default=det_names, key=f"sel_foods_{fname}")
            for n in sel_foods:
                default_qty = 1.0
                for d in detected:
                    if d[0]==n:
                        default_qty = d[1]
                chosen[n] = st.number_input(f"{n} 수량", 0.0, 10.0, default_qty, 0.5, key=f"qty_{fname}_{n}")

            meal = st.selectbox("이 사진은 어느 끼니인가요?", ["점심","저녁","간식"], key=f"meal_{fname}")
            preview_kcal = sum(kcal_of(n, foods_df_idx)*q for n, q in chosen.items())
            st.info(f"이 사진 선택 항목 kcal 미리보기: 약 {int(preview_kcal)} kcal")

            if st.button("선택 항목을 끼니에 추가", key=f"add_from_photo_{fname}"):
                target = {"점심":"lunch", "저녁":"dinner", "간식":"snacks"}[meal]
                for n, q in chosen.items():
                    logs[target].append((n, float(q)))
                logs.setdefault("photos", []).append({"file": path, "meal": target, "items": [(n, float(q)) for n,q in chosen.items()], "preview_kcal": float(preview_kcal)})
                st.success(f"{meal}에 {len(chosen)}개 항목이 추가되었습니다.")

    # ------ Burn ------
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

    # ------ Calculations + Quality ------
    st.subheader("🧮 칼로리 & 품질 계산")
    protein_g = carb_g = fat_g = fiber_g = 0.0
    def add_macros(lst):
        nonlocal protein_g, carb_g, fat_g, fiber_g
        for name, qty in lst:
            p,c,f,fb = macros_of(name, foods_df_idx)
            protein_g += p*qty; carb_g += c*qty; fat_g += f*qty; fiber_g += fb*qty

    bf_kcal = sum(kcal_of(n, foods_df_idx)*amt for n, amt in logs["breakfast_override"].items())
    add_macros([(n, amt) for n, amt in logs["breakfast_override"].items()])
    lunch_kcal = sum(kcal_of(n, foods_df_idx)*qty for n, qty in logs["lunch"])
    add_macros(logs["lunch"])
    dinner_kcal = sum(kcal_of(n, foods_df_idx)*qty for n, qty in logs["dinner"])
    add_macros(logs["dinner"])
    snack_kcal = sum(kcal_of(n, foods_df_idx)*qty for n, qty in logs["snacks"])
    add_macros(logs["snacks"])

    intake = bf_kcal + lunch_kcal + dinner_kcal + snack_kcal
    steps_kcal = st.session_state.profile["step_kcal_factor"] * steps
    ex_kcal = 0.0
    for (ename, qty) in logs["exercises"]:
        row = st.session_state.ex_df[st.session_state.ex_df["운동"]==ename]
        if not row.empty:
            ex_kcal += float(row.iloc[0]["kcal_per_unit"]) * float(qty)
    burn = steps_kcal + ex_kcal

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("아침 kcal", int(bf_kcal))
    with c2: st.metric("점심 kcal", int(lunch_kcal))
    with c3: st.metric("저녁 kcal", int(dinner_kcal))
    with c4: st.metric("간식 kcal", int(snack_kcal))
    with c5: st.metric("총 섭취", int(intake))
    st.metric("소비 칼로리", f"{int(burn)} kcal")
    st.metric("칼로리 밸런스(섭취-소비)", f"{int(intake - burn)} kcal")

    # Diet quality
    score = diet_quality_score(intake, protein_g, carb_g, fat_g, fiber_g)
    st.success(f"식단 품질 점수: **{score}/100**")
    st.caption(f"단백질 {protein_g:.1f}g · 탄수 {carb_g:.1f}g · 지방 {fat_g:.1f}g · 식이섬유 {fiber_g:.1f}g")

    st.subheader("✅ 목표 달성 체크")
    goal = intake <= st.session_state.profile["daily_calorie_goal"]
    done = st.checkbox("오늘 목표 달성", value=bool(logs.get("goal_done", goal)))
    logs["goal_done"] = done
    note = st.text_area("메모", value=logs.get("note",""))
    logs["note"] = note

    st.session_state.logs[key_day] = logs
    st.success("해당 날짜 기록이 임시 저장되었습니다. (브라우저/세션 기준)")

# --- Tab3 ---
with tab3:
    st.markdown("### 🍲 음식 DB (칼로리/영양) — 식이섬유 컬럼 포함")
    st.session_state.foods_df = st.data_editor(st.session_state.foods_df, num_rows="dynamic", use_container_width=True, key="food_editor")
    st.markdown("### 🏃 운동 DB")
    st.session_state.ex_df = st.data_editor(st.session_state.ex_df, num_rows="dynamic", use_container_width=True, key="ex_editor")

# --- Tab4 ---
with tab4:
    st.markdown("### 📈 주간/월간 진행 상황 요약")
    if st.session_state.logs:
        df_rows = []
        for day, lg in st.session_state.logs.items():
            df_rows.append({
                "날짜": day,
                "걸음수": lg.get("steps",0),
                "점심 항목 수": len(lg.get("lunch",[])),
                "저녁 항목 수": len(lg.get("dinner",[])),
                "간식 항목 수": len(lg.get("snacks",[])),
                "목표달성": lg.get("goal_done", False)
            })
        dfp = pd.DataFrame(df_rows).sort_values("날짜")
        st.dataframe(dfp, use_container_width=True)
        streak = dfp["목표달성"].astype(bool).astype(int).rolling(window=7).sum().max()
        st.metric("최근 7일 목표 달성 최대 연속일", int(streak if pd.notna(streak) else 0))
    else:
        st.info("아직 기록이 없습니다. '📝 일일 기록' 탭에서 오늘부터 시작해 보세요!")

# --- Tab5 ---
with tab5:
    st.markdown("### 🖼️ 사진 앨범 / 타임라인")
    if not st.session_state.logs:
        st.info("아직 사진 기록이 없습니다.")
    else:
        # Group by day
        days_sorted = sorted(st.session_state.logs.keys())
        for d in days_sorted:
            lg = st.session_state.logs[d]
            photos = lg.get("photos", [])
            if not photos: 
                continue
            st.subheader(f"{d} ( {weekday_kr(datetime.fromisoformat(d).date())} )")
            cols = st.columns(3)
            total_kcal_day = 0.0
            for i, ph in enumerate(photos):
                with cols[i % 3]:
                    st.image(ph["file"], use_column_width=True)
                    st.caption(f"{ph['meal']} · 미리보기 {int(ph.get('preview_kcal',0))} kcal")
                    total_kcal_day += float(ph.get("preview_kcal",0.0))
            st.write(f"사진 기반 추정 섭취 kcal 합계(미리보기): **{int(total_kcal_day)} kcal**")

st.caption("※ 건강 관련 수치는 일반 참고용입니다. 당뇨 등 질환이 의심되면 반드시 의료진과 상담하세요.")
