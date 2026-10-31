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

# 🔄 FUNCTION TO UPDATE PASSWORD IN EXCEL DATA
def update_excel_password(emp_code, new_password):
    try:
        if os.path.exists(excel_file):
            df = pd.read_excel(excel_file)
            
            # Sahi string cleaning bina kisi syntax error ke
            df['EmployeeCode'] = df['EmployeeCode'].astype(str).str.strip()
            
            # Row index nikalna jahan employee code match ho
            idx = df[df['EmployeeCode'] == str(emp_code).strip()].index
            
            if not idx.empty:
                # Excel me password column update karna
                df.loc[idx, 'Password'] = str(new_password).strip()
                df.to_excel(excel_file, index=False)
                return True
        return False
    except Exception as e:
        st.error(f"Database Error: {e}")
        return False

# 📄 SAFE FUNCTION TO GENERATE COMPLETE PAYSLIP STRUCTURE
def get_html_payslip(emp):
    html_layout = f"""
    <div style="font-family: Arial, sans-serif; padding: 15px; border: 1px solid #CBD5E0; background-color: #FFF; border-radius: 8px;">
        <div style="text-align: center; margin-bottom: 15px;">
            <h2 style="color: #1A365D; margin: 0;">INNOVSHIELD MANAGEMENT PVT. LTD.</h2>
            <p style="color: #4A5568; margin: 3px 0; font-size: 13px;">Qutub Vihar, Dwarka, New Delhi</p>
            <h4 style="margin: 10px 0 0 0; color: #2D3748;">Pay Slip for the Month of: {emp.get('Month', 'N/A')}</h4>
        </div>
        <hr style="border: 0; border-top: 1px solid #E2E8F0; margin-bottom: 15px;"/>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 15px;">
            <tr>
                <td style="padding: 6px;"><b>Emp Code:</b> {emp.get('EmployeeCode', '')}</td>
                <td style="padding: 6px;"><b>Name:</b> {emp.get('Employee Name', '')}</td>
                <td style="padding: 6px;"><b>Designation:</b> {emp.get('Designation', '')}</td>
            </tr>
            <tr>
                <td style="padding: 6px;"><b>Location:</b> {emp.get('Location', '')}</td>
                <td style="padding: 6px;"><b>A/c No:</b> {emp.get('Ac No', '')}</td>
                <td style="padding: 6px;"><b>UAN No:</b> {emp.get('UAN NO', '')}</td>
            </tr>
            <tr>
                <td style="padding: 6px;"><b>ESIC No:</b> {emp.get('ESIC NO', '')}</td>
                <td style="padding: 6px;"><b>Month Days:</b> {emp.get('Month Days', '')}</td>
                <td style="padding: 6px;"><b>Worked Days:</b> {emp.get('Worked Days', '')}</td>
            </tr>
        </table>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; text-align: left;">
            <tr style="background-color: #1A365D; color: white;">
                <th style="padding: 8px; border: 1px solid #CBD5E0;">Salary Component</th>
                <th style="padding: 8px; border: 1px solid #CBD5E0;">Fixed Rate (₹)</th>
                <th style="padding: 8px; border: 1px solid #CBD5E0;">Earned Amount (₹)</th>
                <th style="padding: 8px; border: 1px solid #CBD5E0;">Deductions</th>
                <th style="padding: 8px; border: 1px solid #CBD5E0;">Amount (₹)</th>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Basic Salary</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Fixed Basic', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Earn Basic', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Provident Fund (PF)</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('PF', 0)))}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">HRA</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Fixed HRA', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Earn HRA', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">ESIC</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('ESIC', 0)))}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Statutory Bonus</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Fixed Stat Bonus', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Earn Stat Bon', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">LWF</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('LWF', 0)))}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Special Allowance</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Fixed Special', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Earn Special', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">EWF Deduc</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('EWF', 0)))}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Leave Encashment</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Leave Encash', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Ship/COD Loss</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Ship/COD Loss', 0)))}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Attendance Bonus</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Atte Bonus', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Salary Advance</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Advance', 0)))}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Mobile Allowances</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Mobile Allo', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Notice Pay Deduct</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Notice Pay', 0)))}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Group Incentive</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Group Incentive', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Other Deductions</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Other Deduc', 0)))}</td>
            </tr>
            <tr style="background-color: #EDF2F7; font-weight: bold;">
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Gross Total</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Gross Fixed', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Gross Earned', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Total Deductions</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Total Deduc', 0)))}</td>
            </tr>
        </table>
        <div style="margin-top: 15px; padding: 10px; background-color: #EBF8FF; border-left: 4px solid #3182CE; font-weight: bold; font-size: 14px;">
            Net Payable Salary (Net Take Home): ₹{int(float(emp.get('Net Payable', 0)))}
        </div>
    </div>
    """
    return html_layout

# --- MAIN APP LOGIC ---
if not st.session_state['is_authenticated']:
    st.title("🔒 Employee PaySlip Portal")
    st.subheader("Login to your account")
    
    with st.form("login_form_container"):
        emp_code_input = st.text_input("Employee Code")
        password_input = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login", use_container_width=True)
        
        if login_button:
            if os.path.exists(excel_file):
                df = pd.read_excel(excel_file)
                
                # Pure data strings ko smooth conversion kiya matching ke liye
