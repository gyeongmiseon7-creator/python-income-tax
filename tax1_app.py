import streamlit as st

# 세금 계산 함수
def calculate_income_tax(income):
    tax_brackets = [
        (12000000, 0.06),
        (46000000, 0.15),
        (88000000, 0.24),
        (150000000, 0.35),
        (300000000, 0.38),
        (500000000, 0.40),
        (1000000000, 0.42),
        (float('inf'), 0.45)
    ]

    tax = 0
    previous_limit = 0

    for limit, rate in tax_brackets:
        if income > limit:
            tax += (limit - previous_limit) * rate
            previous_limit = limit
        else:
            tax += (income - previous_limit) * rate
            break

    return tax

# Streamlit 인터페이스
st.title("💰 소득세 계산기")
income = st.number_input("연간 소득을 입력하세요 (원)", min_value=0, step=1000000)

if income:
    tax = calculate_income_tax(income)
    after_tax = income - tax

    st.subheader("📊 결과")
    st.write(f"**총 소득:** {income:,.0f} 원")
    st.write(f"**예상 세금:** {tax:,.0f} 원")
    st.write(f"**세후 소득:** {after_tax:,.0f} 원") 
