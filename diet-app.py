import streamlit as st
from your_script import generate_weekly_meal_plan  # 위 함수 불러오기

st.title("🌿 52세 여성 갱년기 맞춤 다이어트 식단")

if st.button("한 주 식단 생성"):
    plan = generate_weekly_meal_plan()
    for day, meals in plan.items():
        st.subheader(f"{day}요일")
        for meal, items in meals.items():
            st.write(f"**{meal}**: {', '.join(items)}") 
