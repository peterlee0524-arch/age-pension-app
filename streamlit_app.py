import streamlit as st
from datetime import date

st.set_page_config(page_title="Australian Age Pension Calculator", layout="centered")
st.title("Australian Age Pension Calculator (Prototype)")
st.caption("2025 thresholds; demo only—no financial advice.")

def add_years(d: date, years: int) -> date:
    try: return d.replace(year=d.year + years)
    except ValueError: return d.replace(month=3, day=1, year=d.year+years)

st.header("Profile")
dob = st.date_input("Your Date of Birth", value=date(1980,1,1))
is_couple = st.checkbox("Couple?", value=True)
partner_dob = st.date_input("Partner Date of Birth", value=date(1983,1,1)) if is_couple else None
has_home = st.checkbox("Own Home (principal residence)?", value=True)

st.header("Assets & Income")
assets = st.number_input("Assessable Assets (excluding home)", min_value=0.0, step=1000.0, value=700000.0)
weekly_rent = st.number_input("Weekly Gross Rent", min_value=0.0, step=10.0, value=700.0)
rent_expense_rate = st.slider("Rental expense rate (%)", 0, 60, 20)
other_income = st.number_input("Other Income (fortnightly)", min_value=0.0, step=50.0, value=0.0)

# 2025 thresholds
pension_max = 1682.80 if is_couple else 1116.30
if is_couple and has_home:
    assets_full_limit, assets_cut_limit = 481500, 1074000
elif is_couple and not has_home:
    assets_full_limit, assets_cut_limit = 739500, 1332000
elif (not is_couple) and has_home:
    assets_full_limit, assets_cut_limit = 321500, 714500
else:
    assets_full_limit, assets_cut_limit = 579500, 972500
taper_rate = 3.0
income_free = 360 if is_couple else 204
income_rate = 0.25

net_rent_fortnight = weekly_rent * 2 * (1 - rent_expense_rate/100)
income_total = net_rent_fortnight + other_income

# Assets test
if assets <= assets_full_limit:
    pension_assets = pension_max
elif assets >= assets_cut_limit:
    pension_assets = 0
else:
    excess = assets - assets_full_limit
    reduction = (excess/1000)*taper_rate
    pension_assets = max(pension_max - reduction, 0)

# Income test
if income_total <= income_free:
    pension_income = pension_max
else:
    excess = income_total - income_free
    reduction = excess * income_rate * (2 if is_couple else 1)
    pension_income = max(pension_max - reduction, 0)

final_pension = min(pension_assets, pension_income)

st.header("Results")
st.write(f"Assets test (fortnight): ${pension_assets:,.2f}")
st.write(f"Income test (fortnight): ${pension_income:,.2f}")
st.success(f"Final pension (fortnight): ${final_pension:,.2f}  |  Annual: ${final_pension*26:,.2f}")
