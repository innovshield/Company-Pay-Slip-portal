import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="Corporate PaySlip Portal", page_icon="🔒", layout="centered")

# 🔒 HACK TO HIDE STREAMLIT TOOLBAR, FOOTER & CORNER SETTINGS MENU FOR EMPLOYEES
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    stDecoration {display:none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important;}
    .viewerBadge_container__174fd {display: none !important;}
    </style>
    """, unsafe_allow_html=True)

# 1. INITIALIZE SESSION STATES FOR PRIVATE LOGIN
if 'is_authenticated' not in st.session_state:
    st.session_state['is_authenticated'] = False
if 'logged_in_user' not in st.session_state:
    st.session_state['logged_in_user'] = None

excel_file = "salary_data.xlsx"

# 📄 SAFE FUNCTION TO GENERATE COMPLETE PAYSLIP STRUCTURE
def get_html_payslip(emp):
    # Function to validate and clean numeric data (handles NaNs and blanks safely)
    def clean_val(key):
        val = emp.get(key, 0)
        return 0 if pd.isna(val) else float(val)

    # Fetch and clean raw values
    basic = clean_val('Basic')
    hra = clean_val('HRA')
    allowance = clean_val('Special Allowance')
    deductions = clean_val('Deductions')
    
    # Calculate Dynamic Totals
    gross_earnings = basic + hra + allowance
    net_salary = gross_earnings - deductions

    # 🌟 DYNAMICALLY GENERATE ROWS ONLY IF COMPONENT VALUE > 0
    earnings_rows = []
    if basic > 0:
        earnings_rows.append(f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #EDF2F7;">Basic Salary</td>
                <td style="padding: 8px; text-align: right; border-bottom: 1px solid #EDF2F7;">{basic:,.2f}</td>
            </tr>
        """)
    if hra > 0:
        earnings_rows.append(f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #EDF2F7;">HRA</td>
                <td style="padding: 8px; text-align: right; border-bottom: 1px solid #EDF2F7;">{hra:,.2f}</td>
            </tr>
        """)
    if allowance > 0:
        earnings_rows.append(f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #EDF2F7;">Special Allowance</td>
                <td style="padding: 8px; text-align: right; border-bottom: 1px solid #EDF2F7;">{allowance:,.2f}</td>
            </tr>
        """)

    deductions_rows = []
    if deductions > 0:
        deductions_rows.append(f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #EDF2F7;">Deductions / Loss of Pay</td>
                <td style="padding: 8px; text-align: right; border-bottom: 1px solid #EDF2F7;">{deductions:,.2f}</td>
            </tr>
        """)

    # Combine the arrays into strings safely
    earnings_html = "".join(earnings_rows) if earnings_rows else "<tr><td colspan='2' style='padding: 8px; text-align: center; color: #A0AEC0;'>No Earnings This Cycle</td></tr>"
    deductions_html = "".join(deductions_rows) if deductions_rows else "<tr><td colspan='2' style='padding: 8px; text-align: center; color: #A0AEC0;'>No Deductions This Cycle</td></tr>"

    html_layout = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #CBD5E0; background-color: #FFF; border-radius: 8px; color: #333;">
        <div style="text-align: center; margin-bottom: 15px;">
            <h2 style="color: #1A365D; margin: 0;">INNOVSHIELD MANAGEMENT PVT. LTD.</h2>
            <p style="color: #4A5568; margin: 3px 0; font-size: 13px;">Qutub Vihar, Dwarka, New Delhi</p>
            <h4 style="margin: 10px 0 0 0; color: #2D3748;">Pay Slip for the Month of: {emp.get('Month', 'N/A')}</h4>
        </div>
        <hr style="border: 0; border-top: 1px solid #E2E8F0; margin-bottom: 15px;"/>
        
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 20px;">
            <tr>
                <td style="padding: 6px; width: 33%;"><b>Emp Code:</b> {emp.get('EmployeeCode', '')}</td>
                <td style="padding: 6px; width: 33%;"><b>Name:</b> {emp.get('Employee Name', '')}</td>
                <td style="padding: 6px; width: 33%;"><b>Designation:</b> {emp.get('Designation', '')}</td>
            </tr>
        </table>
        
        <!-- TWO COLUMN BLOCK FOR SIDE-BY-SIDE TABLES -->
        <div style="display: flex; gap: 20px; margin-bottom: 15px;">
            <!-- Earnings Block -->
            <div style="flex: 1;">
                <table style="width: 100%; border-collapse: collapse; font-size: 13px; border: 1px solid #E2E8F0;">
                    <tr style="background-color: #F7FAFC; border-bottom: 1px solid #E2E8F0;">
                        <th style="padding: 8px; text-align: left;">Earnings</th>
                        <th style="padding: 8px; text-align: right; width: 100px;">Amount (₹)</th>
                    </tr>
                    {earnings_html}
                    <tr style="background-color: #EDF2F7; font-weight: bold;">
                        <td style="padding: 8px;">Gross Earnings</td>
                        <td style="padding: 8px; text-align: right;">{gross_earnings:,.2f}</td>
                    </tr>
                </table>
            </div>
            
            <!-- Deductions Block -->
            <div style="flex: 1;">
                <table style="width: 100%; border-collapse: collapse; font-size: 13px; border: 1px solid #E2E8F0;">
                    <tr style="background-color: #F7FAFC; border-bottom: 1px solid #E2E8F0;">
                        <th style="padding: 8px; text-align: left;">Deductions</th>
                        <th style="padding: 8px; text-align: right; width: 100px;">Amount (₹)</th>
                    </tr>
                    {deductions_html}
                    <tr style="background-color: #EDF2F7; font-weight: bold;">
                        <td style="padding: 8px;">Total Deductions</td>
                        <td style="padding: 8px; text-align: right;">{deductions:,.2f}</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <div style="background-color: #EBF8FF; padding: 12px; border-radius: 6px; text-align: right; font-size: 15px;">
            <b style="color: #2B6CB0;">Net Take-Home Salary: ₹{net_salary:,.2f}</b>
        </div>
    </div>
    """
    return html_layout

# 2. HELPER TO LOAD EXCEL DATA
def load_data():
    if os.path.exists(excel_file):
        try:
            return pd.read_excel(excel_file)
        except Exception as e:
            st.error(f"Error reading database file: {e}")
            return None
    else:
        st.warning(f"Database sheet '{excel_file}' not found. Please place it in the application directory.")
        return None

# 3. INTERFACE ROUTING
df = load_data()

if not st.session_state['is_authenticated']:
    # 📑 LOGIN VIEW
    st.markdown("<h2 style='text-align: center; color: #1A365D;'>Employee Self-Service</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #718096;'>Enter your Employee Code to access your monthly payslip safely.</p>", unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        emp_code_input = st.text_input("Employee Code", placeholder="e.g., ISM-101").strip()
        submit_btn = st.form_submit_button("Verify & Access Portal")
        
        if submit_btn:
            if not emp_code_input:
                st.error("Please enter a valid Employee Code.")
            elif df is not None:
                matched_user = df[df['EmployeeCode'].astype(str) == emp_code_input]
                
                if not matched_user.empty:
                    st.session_state['is_authenticated'] = True
                    st.session_state['logged_in_user'] = emp_code_input
                    st.rerun()
                else:
                    st.error("Invalid Employee Code. Please check and try again.")
else:
    # 📑 DASHBOARD VIEW (AUTHENTICATED)
    current_user_code = st.session_state['logged_in_user']
    user_records = df[df['EmployeeCode'].astype(str) == current_user_code]
    
    # Grab user metadata safely using .iloc
    user_first_record = user_records.iloc[0].to_dict()
    
    # Fixed columns layout (Streamlit 2 columns fix)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### Welcome, **{user_first_record.get('Employee Name', 'Employee')}**")
    with col2:
        if st.button("Log Out", use_container_width=True):
            st.session_state['is_authenticated'] = False
            st.session_state['logged_in_user'] = None
            st.rerun()
            
    st.divider()
    
    available_months = user_records['Month'].dropna().unique()
    
    if len(available_months) == 0:
        st.info("No active monthly statements found associated with your profile details.")
    else:
        selected_month = st.selectbox("Select Statement Cycle / Month", options=available_months)
        
        final_record = user_records[user_records['Month'] == selected_month].iloc[0].to_dict()
        
        # Render the HTML Formatted Payslip
        st.markdown(get_html_payslip(final_record), unsafe_allow_html=True)
