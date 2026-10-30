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

# 📄 SAFE HTML-BASED PAYSLIP GENERATION (Removes ReportLab crashes completely)
def convert_to_html_slip(emp):
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; color: #333; }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            .title {{ color: #1A365D; font-size: 20px; font-weight: bold; }}
            .subtitle {{ color: #4A5568; font-size: 12px; }}
            .info-table, .salary-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 12px; }}
            .info-table td, .salary-table th, .salary-table td {{ border: 1px solid #CBD5E0; padding: 8px; text-align: left; }}
            .salary-table th {{ background-color: #1A365D; color: white; }}
            .net-pay {{ background-color: #EBF8FF; color: #2B6CB0; font-weight: bold; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">INNOVSHIELD MANAGEMENT PVT. LTD.</div>
            <div class="subtitle">Qutub Vihar, Dwarka, New Delhi</div>
            <h3>Pay Slip for the Month of: {emp.get('Month', 'N/A')}</h3>
        </div>
        
        <table class="info-table">
            <tr>
                <td><b>Emp Code:</b> {emp.get('EmployeeCode', '')}</td>
                <td><b>Name:</b> {emp.get('Employee Name', '')}</td>
                <td><b>Designation:</b> {emp.get('Designation', '')}</td>
            </tr>
            <tr>
                <td><b>Location:</b> {emp.get('Location', '')}</td>
                <td><b>A/c No:</b> {emp.get('Ac No', '')}</td>
                <td><b>UAN No:</b> {emp.get('UAN NO', '')}</td>
            </tr>
            <tr>
                <td><b>ESIC No:</b> {emp.get('ESIC NO', '')}</td>
                <td><b>Month Days:</b> {emp.get('Month Days', '')}</td>
                <td><b>Worked Days:</b> {emp.get('Worked Days', '')}</td>
            </tr>
        </table>

        <table class="salary-table">
            <tr>
                <th>Salary Component</th>
                <th>Fixed Rate (₹)</th>
                <th>Earned Amount (₹)</th>
                <th>Deductions</th>
                <th>Amount (₹)</th>
            </tr>
            <tr>
                <td>Basic Salary</td>
                <td>{int(float(emp.get('Fixed Basic', 0)))}</td>
                <td>{int(float(emp.get('Earn Basic', 0)))}</td>
                <td>Provident Fund (PF)</td>
                <td>{int(float(emp.get('PF', 0)))}</td>
            </tr>
            <tr>
                <td>HRA</td>
                <td>{int(float(emp.get('Fixed HRA', 0)))}</td>
                <td>{int(float(emp.get('Earn HRA', 0)))}</td>
                <td>ESIC</td>
                <td>{int(float(emp.get('ESIC', 0)))}</td>
            </tr>
            <tr class="net-pay">
                <td colspan="3">NET PAYABLE TAKE-HOME SALARY</td>
                <td colspan="2" style="text-align: center;">₹{int(float(emp.get('Net Pay', 0)))}</td>
            </tr>
        </table>
        <p style="font-size: 10px; font-style: italic;">Note: This is a system-generated secure slip and does not require a physical stamp or signature.</p>
    </body>
    </html>
    """
    return html_content

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
                    # Pure single row processing flat extraction index 0 safe lookup
                    emp_data_list = target_df.to_dict(orient='records')
                    emp_data = emp_data_list[0]
                    
                    st.subheader(f"👋 Welcome, {emp_data.get('Employee Name', 'Employee')}")
                    st.write(f"**Designation:** {emp_data.get('Designation', 'N/A')} | **Selected Month:** {selected_month}")
                    
                    st.markdown("---")
                    
                    # Generate safe html data slip format
                    slip_html = convert_to_html_slip(emp_data)
                    
                    # 📥 BIG BLUE SECURE STREAMLIT DOWNLOAD BUTTON
                    st.download_button(
                        label=f"📥 Click Here to Download PaySlip ({selected_month}) - HTML PDF Format",
                        data=slip_html,
                        file_name=f"PaySlip_{current_emp}_{selected_month}.html",
                        mime="text/html",
                        use_container_width=True
                    )
                    
                    st.markdown("---")
                    
                    # Dashboard Metrics Summary Panels
                    st.markdown("### 📊 Salary Overview Dashboard")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Gross Earnings", f"₹{int(float(emp_data.get('Total Earn', 0)))}")
                    c2.metric("Total Deductions", f"₹{int(float(emp_data.get('Total Dedu', 0)))}")
                    c3.metric("Net Take-Home", f"₹{int(float(emp_data.get('Net Pay', 0)))}")
                else:
                    st.error("❌ Selected month ka data nahi mila.")
            else:
                st.error("❌ Employee records database matching error.")
                
        with tab2:
            st.subheader("🛠️ Account Security Settings")
            st.write("Aap yahan se apna login password secure tarike se change kar sakte hain:")
            
            with st.form("change_password_form"):
                current_password_input = st.text_input("Current Password:", type="password").strip()
                new_password_input = st.text_input("New Password:", type="password").strip()
                confirm_password_input = st.text_input("Confirm New Password:", type="password").strip()
                submit_pass_btn = st.form_submit_button("Update Password 🔐")
                
                if submit_pass_btn:
                    emp_matches = df[df['EmployeeCode'] == current_emp]
                    
                    if not emp_matches.empty:
                        emp_matches_list = emp_matches.to_dict(orient='records')
                        actual_old_pass = str(emp_matches_list[0].get('Password', '')).strip()
                        
                        if current_password_input != actual_old_pass:
                            st.error("❌ Current Password galat hai! Kripya sahi password dalein.")
                        elif new_password_input != confirm_password_input:
                            st.error("❌ Naya password aur confirm password match nahi ho raha!")
                        elif len(new_password_input) < 4:
