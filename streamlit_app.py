import streamlit as st

st.set_page_config(page_title="소득세 계산기", page_icon="💰")

st.title("💰 소득세 계산기")
st.caption("단순 예시용 세율(고:30% / 중:20% / 저:10%)으로 계산합니다.")

# 사용자 입력 (만원 단위)
income = st.number_input("소득(만원)", min_value=0, step=100, value=20000)

# 조건문으로 소득 수준 분류 (요청하신 기존 로직 유지)
if income >= 10000:
    tax = income * 0.3
    level = "고소득층"
elif income >= 5000:
    tax = income * 0.2
    level = "중간소득층"
else:
    tax = income * 0.1
    level = "저소득층"

# 결과 표시
st.subheader("결과")
col1, col2, col3 = st.columns(3)
col1.metric("소득(만원)", f"{income:,.0f}")
col2.metric("소득 수준", level)
col3.metric("세금(만원)", f"{tax:,.1f}")

# 로그 보기용(선택): 필요하다면 코드/값을 디버깅 영역에 출력
with st.expander("계산 상세 보기"):
    st.code(
        f"""
# 기준 세율
# 고소득: 30%, 중간소득: 20%, 저소득: 10%

income = {income}
if income >= 10000:
    tax = income * 0.3
    level = "고소득층"
elif income >= 5000:
    tax = income * 0.2
    level = "중간소득층"
else:
    tax = income * 0.1
    level = "저소득층"

세금 = {tax}
""",
        language="python",
    )
