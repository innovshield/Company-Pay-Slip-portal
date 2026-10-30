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

EXCEL_FILE = "salary_data.xlsx"

# 📄 SAFE FUNCTION TO GENERATE COMPLETE PAYSLIP STRUCTURE
def get_html_payslip(emp):
    html_layout = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #CBD5E0; background-color: #FFF; border-radius: 8px; color: #000;">
        <div style="text-align: center; margin-bottom: 15px;">
            <h2 style="color: #1A365D; margin: 0;">INNOVSHIELD MANAGEMENT PVT. LTD.</h2>
            <p style="color: #4A5568; margin: 3px 0; font-size: 13px;">Qutub Vihar, Dwarka, New Delhi</p>
            <h4 style="margin: 10px 0 0 0; color: #2D3748;">Pay Slip for the Month of: {emp.get('Month', 'N/A')}</h4>
        </div>
        <hr style="border: 0; border-top: 1px solid #E2E8F0; margin-bottom: 15px;"/>
        
        <!-- Employee Details Table -->
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 20px;">
            <tr>
                <td style="padding: 6px; width: 33%;"><b>Emp Code:</b> {emp.get('EmployeeCode', '')}</td>
                <td style="padding: 6px; width: 33%;"><b>Name:</b> {emp.get('Employee Name', '')}</td>
                <td style="padding: 6px; width: 34%;"><b>Designation:</b> {emp.get('Designation', '')}</td>
            </tr>
            <tr>
                <td style="padding: 6px;"><b>Bank Name:</b> {emp.get('Bank Name', 'N/A')}</td>
                <td style="padding: 6px;"><b>A/C No:</b> {emp.get('Account Number', 'N/A')}</td>
                <td style="padding: 6px;"><b>PAN:</b> {emp.get('PAN', 'N/A')}</td>
            </tr>
        </table>

        <!-- Earnings & Deductions Breakup -->
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; border: 1px solid #E2E8F0;">
            <thead>
                <tr style="background-color: #F7FAFC; border-bottom: 1px solid #E2E8F0;">
                    <th style="padding: 8px; text-align: left; border-right: 1px solid #E2E8F0;">Earnings</th>
                    <th style="padding: 8px; text-align: right; border-right: 1px solid #E2E8F0;">Amount (₹)</th>
                    <th style="padding: 8px; text-align: left; border-right: 1px solid #E2E8F0;">Deductions</th>
                    <th style="padding: 8px; text-align: right;">Amount (₹)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 8px; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;">Basic Salary</td>
                    <td style="padding: 8px; text-align: right; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;">{emp.get('Basic', 0):,.2f}</td>
                    <td style="padding: 8px; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;">Provident Fund (PF)</td>
                    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #E2E8F0;">{emp.get('PF', 0):,.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;">House Rent Allowance (HRA)</td>
                    <td style="padding: 8px; text-align: right; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;">{emp.get('HRA', 0):,.2f}</td>
                    <td style="padding: 8px; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;">Professional Tax (PT)</td>
                    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #E2E8F0;">{emp.get('PT', 0):,.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;">Special Allowance</td>
                    <td style="padding: 8px; text-align: right; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;">{emp.get('Special Allowance', 0):,.2f}</td>
                    <td style="padding: 8px; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;">TDS / Income Tax</td>
                    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #E2E8F0;">{emp.get('TDS', 0):,.2f}</td>
                </tr>
                <tr style="background-color: #EDF2F7; font-weight: bold;">
                    <td style="padding: 8px; border-right: 1px solid #E2E8F0;">Gross Earnings</td>
                    <td style="padding: 8px; text-align: right; border-right: 1px solid #E2E8F0;">{emp.get('Gross Earnings', 0):,.2f}</td>
                    <td style="padding: 8px; border-right: 1px solid #E2E8F0;">Total Deductions</td>
                    <td style="padding: 8px; text-align: right;">{emp.get('Total Deductions', 0):,.2f}</td>
                </tr>
            </tbody>
        </table>

        <!-- Net Pay Banner -->
        <div style="margin-top: 20px; padding: 12px; background-color: #EBF8FF; border: 1px solid #BEE3F8; border-radius: 6px; text-align: center;">
            <span style="font-size: 16px; color: #2B6CB0; font-weight: bold;">NET TAKE-HOME PAY: ₹{emp.get('Net Salary', 0):,.2f}</span>
        </div>
        
        <div style="margin-top: 25px; text-align: right; font-size: 11px; color: #A0AEC0;">
            <p>This is a computer-generated document and does not require a physical signature.</p>
        </div>
    </div>
    """
    return html_layout

# 📄 HELPER FUNCTION TO READ DATA SAFELY
def load_salary_data():
    if not os.path.exists(EXCEL_FILE):
        return None
    try:
        return pd.read_excel(EXCEL_FILE)
    except Exception:
        return None

# MAIN APP INTERFACE LOOP
df = load_salary_data()

if df is None:
    st.error(f"⚠️ Initialization Error: The database layout data file `{EXCEL_FILE}` was not found or is unreadable. Please contact HR.")
else:
    # Ensure standard schema items are strings for matching
    df['EmployeeCode'] = df['EmployeeCode'].astype(str).str.strip()
    df['Password'] = df['Password'].astype(str).str.strip()

    if not st.session_state['is_authenticated']:
        st.subheader("🔒 Employee Self-Service Login")
        
        with st.form("login_form"):
            emp_code = st.text_input("Employee Code").strip()
            password = st.text_input("Password", type="password").strip()
            submit_button = st.form_submit_button("Authenticate")
            
            if submit_button:
                # Find matching user rows
                match = df[(df['EmployeeCode'] == emp_code) & (df['Password'] == password)]
                if not match.empty:
                    st.session_state['is_authenticated'] = True
                    st.session_state['logged_in_user'] = match.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("Invalid Employee Code or Password. Please try again.")
    else:
        current_user = st.session_state['logged_in_user']
        
        # Dashboard Header
        col1, col2 = st.columns([4, 1])
        with col1:
            st.success(f"Welcome, {current_user['Employee Name']} 👋")
        with col2:
            if st.button("Log Out"):
                st.session_state['is_authenticated'] = False
                st.session_state['logged_in_user'] = None
                st.rerun()
        
        # Render dynamic payslip HTML view securely inside markdown container
        payslip_html = get_html_payslip(current_user)
        st.markdown(payslip_html, unsafe_allow_html=True)
        
        # Download Option
        st.write("")
        st.download_button(
            label="📥 Download PaySlip Summary (Text Format)",
            data=f"INNOVSHIELD MANAGEMENT PVT. LTD.\n"
                 f"Pay Slip for: {current_user.get('Month')}\n"
                 f"Employee: {current_user.get('Employee Name')} ({current_user.get('EmployeeCode')})\n"
                 f"Net Take-Home Pay: ₹{current_user.get('Net Salary', 0):,.2f}",
            file_name=f"Payslip_{current_user.get('EmployeeCode')}_{current_user.get('Month')}.txt",
            mime="text/plain"
        )
