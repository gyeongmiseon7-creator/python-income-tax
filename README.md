import streamlit as st
import requests

st.title("🌤 실시간 날씨 정보 (Open-Meteo API)")

# 🔹 1. 사용자 입력
st.subheader("📍 지역 설정")
city = st.text_input("도시 이름을 입력하세요 (예: Seoul, Busan, Tokyo, London):", "Seoul")

# 간단한 도시별 좌표 예시 (필요시 더 추가 가능)
city_coords = {
    "Seoul": (37.57, 126.98),
    "Busan": (35.18, 129.07),
    "Tokyo": (35.68, 139.76),
    "New York": (40.71, -74.01),
    "London": (51.51, -0.13),
}

# 🔹 2. 위도·경도 가져오기
if city in city_coords:
    latitude, longitude = city_coords[city]
else:
    st.warning("등록된 도시가 아니에요. 위·경도를 직접 입력하세요.")
    latitude = st.number_input("위도(latitude)", value=37.57)
    longitude = st.number_input("경도(longitude)", value=126.98)

# 🔹 3. 버튼 클릭 시 API 호출
if st.button("날씨 조회"):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            current = data.get("current_weather", {})

            # 🔸 결과 표시
            st.success(f"🌍 {city} 현재 날씨")
            st.metric("🌡 온도 (°C)", current.get("temperature"))
            st.metric("💨 풍속 (km/h)", current.get("windspeed"))
            st.metric("🧭 풍향 (°)", current.get("winddirection"))
            st.caption(f"⏰ 업데이트 시각: {current.get('time')}")
        else:
            st.error(f"API 요청 실패: {response.status_code}")
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
