import streamlit as st
import requests

st.title("?? �ǽð� ���� ���� (Open-Meteo API)")

# ?? 1. ����� �Է�
st.subheader("?? ���� ����")
city = st.text_input("���� �̸��� �Է��ϼ��� (��: Seoul, Busan, Tokyo, London):", "Seoul")

# ������ ���ú� ��ǥ ���� (�ʿ�� �� �߰� ����)
city_coords = {
    "Seoul": (37.57, 126.98),
    "Busan": (35.18, 129.07),
    "Tokyo": (35.68, 139.76),
    "New York": (40.71, -74.01),
    "London": (51.51, -0.13),
}

# ?? 2. �������浵 ��������
if city in city_coords:
    latitude, longitude = city_coords[city]
else:
    st.warning("��ϵ� ���ð� �ƴϿ���. �����浵�� ���� �Է��ϼ���.")
    latitude = st.number_input("����(latitude)", value=37.57)
    longitude = st.number_input("�浵(longitude)", value=126.98)

# ?? 3. ��ư Ŭ�� �� API ȣ��
if st.button("���� ��ȸ"):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            current = data.get("current_weather", {})

            # ?? ��� ǥ��
            st.success(f"?? {city} ���� ����")
            st.metric("?? �µ� (��C)", current.get("temperature"))
            st.metric("?? ǳ�� (km/h)", current.get("windspeed"))
            st.metric("?? ǳ�� (��)", current.get("winddirection"))
            st.caption(f"? ������Ʈ �ð�: {current.get('time')}")
        else:
            st.error(f"API ��û ����: {response.status_code}")
    except Exception as e:
        st.error(f"�����͸� �ҷ����� �� ������ �߻��߽��ϴ�: {e}")
