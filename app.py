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

# 📄 DYNAMIC HTML PAYSLIP GENERATION FUNCTION (All Components Included Dynamically)
def get_html_payslip(emp):
    # Master Matrix Breakdown Configuration for All Components
    all_components = [
        ("Basic Salary", "Fixed Basic", "Earn Basic", "Provident Fund (PF)", "PF"),
        ("HRA", "Fixed HRA", "Earn HRA", "ESIC", "ESIC"),
        ("Statutory Bonus", "Fixed Stat Bonus", "Earn Stat Bon", "LWF", "LWF"),
        ("Special Allowance", "Fixed Special", "Earn Special", "EWF Deduc", "EWF"),
        ("Leave Encashment", None, "Leave Encash", "Ship/COD Loss", "Ship/COD Loss"),
        ("Attendance Bonus", None, "Atte Bonus", "Salary Advance", "Advance"),
        ("Mobile Allowance", None, "Mobile Allo", "Notice Pay Deduct", "Notice Pay"),
        ("Special Incentive", None, "Special Incentive", None, None),
        ("Group Incentive", None, "Group Incentive", None, None),
        ("Arrears / Other", None, "Arrears", None, None),
        ("Incentive / Performance", None, "Incentive", None, None)
    ]
    
    # Building Dynamic Rows safely
    rows_html = ""
    for comp, f_key, e_key, ded, d_key in all_components:
        f_val = float(emp.get(f_key, 0)) if f_key and emp.get(f_key) else 0.0
        e_val = float(emp.get(e_key, 0)) if e_key and emp.get(e_key) else 0.0
        d_val = float(emp_data.get(d_key, 0)) if d_key and emp_data.get(d_key) else 0.0 if 'emp_data' in globals() else 0.0
        # Multi-month fallback patch
        if d_key:
            try: d_val = float(emp.get(d_key, 0))
            except: d_val = 0.0

        if f_val == 0.0 and e_val == 0.0 and d_val == 0.0 and not ded:
            continue
            
        f_text = str(int(f_val)) if f_key and f_val > 0 else "-"
        e_text = str(int(e_val)) if e_val > 0 else "-"
        d_text = str(int(d_val)) if d_key and d_val > 0 else "-"
        ded_text = ded if ded and (d_val > 0 or comp in ["Basic Salary", "HRA"]) else ""
        comp_text = comp if (f_val > 0 or e_val > 0 or comp in ["Basic Salary", "HRA"]) else ""
        
        if comp_text == "" and ded_text == "":
            continue
            
        rows_html += f"""
        <tr>
            <td style="padding: 6px; border: 1px solid #CBD5E0;">{comp_text}</td>
            <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{f_text}</td>
            <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{e_text}</td>
            <td style="padding: 6px; border: 1px solid #CBD5E0;">{ded_text}</td>
            <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{d_text if ded_text else ""}</td>
        </tr>
        """

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
                <th style="padding: 8px; border: 1px solid #CBD5E0; text-align: center;">Fixed Rate (₹)</th>
                <th style="padding: 8px; border: 1px solid #CBD5E0; text-align: center;">Earned Amount (₹)</th>
                <th style="padding: 8px; border: 1px solid #CBD5E0;">Deductions</th>
                <th style="padding: 8px; border: 1px solid #CBD5E0; text-align: center;">Amount (₹)</th>
            </tr>
            {rows_html}
            <tr style="background-color: #F7FAFC; font-weight: bold;">
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Gross Total</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0; text-align: center;">{int(float(emp.get('Fixed Gross', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0; text-align: center;">{int(float(emp.get('Total Earn', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Total Deduction</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0; text-align: center;">{int(float(emp.get('Total Dedu', 0)))}</td>
            </tr>
            <tr style="background-color: #EBF8FF; color: #2B6CB0; font-weight: bold; font-size: 14px;">
                <td colspan="3" style="padding: 10px; border: 1px solid #CBD5E0;">NET PAYABLE TAKE-HOME SALARY</td>
                <td colspan="2" style="padding: 10px; border: 1px solid #CBD5E0; text-align: center;">₹{int(float(emp.get('Net Pay', 0)))}</td>
            </tr>
        </table>
        <p style="font-size: 11px; font-style: italic; margin-top: 15px; color: #718096;">Note: This is a system-generated secure slip and does not require a physical stamp or signature.</p>
    </div>
    """
    return html_layout

# --- SECURE DATA GATEKEEPER & WORKSPACE ROUTING ---
if not os.path.exists(excel_file):
    st.error(f"❌ Master Database File '{excel_file}' missing from server root directory.")
else:
    df = pd.read_excel(excel_file)
    df.fillna(0, inplace=True)
    
    for col in ['EmployeeCode', 'Password', 'Employee Name', 'Month']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if not st.session_state['is_authenticated']:
        st.title("🔒 Secure Corporate PaySlip Portal")
        st.subheader("Login required to access the application")
        
        with st.form("portal_gateway_login"):
            input_user = st.text_input("Employee Code:").strip()
            input_pass = st.text_input("Password:", type="password").strip()
            login_btn = st.form_submit_button("Access Portal")
            
            if login_btn:
                if input_user and input_pass:
                    match = df[(df['EmployeeCode'] == input_user) & (df['Password'] == input_pass)]
                    if not match.empty:
                        st.session_state['is_authenticated'] = True
                        st.session_state['logged_in_user'] = input_user
                        st.success("Authorized! Loading profile dashboard...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Employee Code or Password.")
                else:
                    st.warning("Please fill in both fields.")
    else:
        st.title("🔒 Secure Corporate PaySlip Portal")
        
        st.sidebar.title("🔐 Secure Session")
        st.sidebar.write(f"Account: **{st.session_state['logged_in_user']}**")
        if st.sidebar.button("Logout Session 🚪"):
            st.session_state['is_authenticated'] = False
            st.session_state['logged_in_user'] = None
            st.rerun()
            
        tab1, tab2 = st.tabs(["🔑 Employee Login Portal", "🔄 Change Password"])
        current_emp = st.session_state['logged_in_user']
        
        with tab1:
            user_records = df[df['EmployeeCode'] == current_emp]
            
            if not user_records.empty:
                available_months = user_records['Month'].unique().tolist()
                selected_month = st.selectbox("Select Month for PaySlip:", available_months)
                
                target_df = user_records[user_records['Month'] == selected_month]
                
                if not target_df.empty:
                    # Pure positional first match item extract
                    emp_data = target_df.iloc[0].to_dict()
                    
