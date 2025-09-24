import streamlit as st
from datetime import date

st.set_page_config(page_title="Australian Age Pension Calculator", layout="centered")
st.title("Australian Age Pension Calculator (Prototype)")
st.caption("2025 thresholds; demo only—no financial advice.")

def calc_pension(assets, weekly_rent, rent_expense_rate, other_income, is_couple, has_home):
    # pension thresholds
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

    # income calc
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

    return min(pension_assets, pension_income)

# ---------------- Profile ----------------
st.header("Profile")
dob = st.date_input("Your Date of Birth", value=date(1980,1,1))
is_couple = st.checkbox("Couple?", value=True)
partner_dob = st.date_input("Partner Date of Birth", value=date(1983,1,1)) if is_couple else None
has_home = st.checkbox("Own Home (principal residence)?", value=True)

# ---------------- Baseline Inputs ----------------
st.header("Baseline Assets & Income")
assets = st.number_input("Assessable Assets (excluding home)", min_value=0.0, step=1000.0, value=700000.0)
weekly_rent = st.number_input("Weekly Gross Rent", min_value=0.0, step=10.0, value=700.0)
rent_expense_rate = st.slider("Rental expense rate (%)", 0, 60, 20)
other_income = st.number_input("Other Income (fortnightly)", min_value=0.0, step=50.0, value=0.0)

# ---------------- Scenario Simulator ----------------
st.sidebar.header("Scenario Simulator")
sell_property = st.sidebar.number_input("Sell property (asset reduction $)", 0.0, 5_000_000.0, 0.0, 1000.0)
gift_cash = st.sidebar.number_input("Gift cash to children ($)", 0.0, 5_000_000.0, 0.0, 1000.0)
rent_delta = st.sidebar.number_input("Change weekly rent (+/- $)", -1000.0, 1000.0, 0.0, 10.0)

assets_scenario = max(0.0, assets - sell_property - gift_cash)
weekly_rent_scenario = max(0.0, weekly_rent + rent_delta)

# ---------------- Results ----------------
baseline_pension = calc_pension(assets, weekly_rent, rent_expense_rate, other_income, is_couple, has_home)
scenario_pension = calc_pension(assets_scenario, weekly_rent_scenario, rent_expense_rate, other_income, is_couple, has_home)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Baseline")
    st.write(f"Assets: ${assets:,.0f}")
    st.write(f"Weekly Rent: ${weekly_rent:,.0f}")
    st.success(f"Pension (fortnight): ${baseline_pension:,.2f}")
    st.info(f"Annual Pension: ${baseline_pension*26:,.2f}")

with col2:
    st.subheader("Scenario")
    st.write(f"Assets: ${assets_scenario:,.0f}")
    st.write(f"Weekly Rent: ${weekly_rent_scenario:,.0f}")
    if gift_cash > 10000:
        st.warning("⚠️ Gifts above $10k per year are still counted for 5 years.")
    st.success(f"Pension (fortnight): ${scenario_pension:,.2f}")
    st.info(f"Annual Pension: ${scenario_pension*26:,.2f}")
