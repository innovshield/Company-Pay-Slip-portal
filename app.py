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

# 📄 SAFE CSV/TEXT PAYSLIP GENERATION (Completely removes ReportLab crashes)
def generate_text_slip(emp_data):
    output = io.StringIO()
    output.write("==================================================\n")
    output.write("          INNOVSHIELD MANAGEMENT PVT. LTD.        \n")
    output.write("            Qutub Vihar, Dwarka, New Delhi        \n")
    output.write("==================================================\n")
    output.write(f"Pay Slip for the Month of: {emp_data.get('Month', 'N/A')}\n\n")
    output.write(f"Emp Code: {emp_data.get('EmployeeCode', '')}\n")
    output.write(f"Name: {emp_data.get('Employee Name', '')}\n")
    output.write(f"Designation: {emp_data.get('Designation', '')}\n")
    output.write(f"Location: {emp_data.get('Location', '')}\n")
    output.write(f"Bank A/c No: {emp_data.get('Ac No', '')}\n")
    output.write(f"UAN No: {emp_data.get('UAN NO', '')}\n\n")
    output.write("--------------------------------------------------\n")
    output.write(f"GROSS TOTAL: RS. {int(float(emp_data.get('Fixed Gross', 0)))}\n")
    output.write(f"TOTAL EARNED: RS. {int(float(emp_data.get('Total Earn', 0)))}\n")
    output.write(f"TOTAL DEDUCTIONS: RS. {int(float(emp_data.get('Total Dedu', 0)))}\n")
    output.write("--------------------------------------------------\n")
    output.write(f"NET PAYABLE TAKE-HOME: RS. {int(float(emp_data.get('Net Pay', 0)))}\n")
    output.write("==================================================\n")
    return output.getvalue()

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
                    # Flat record dictionary mapping
                    records_list = target_df.to_dict(orient='records')
                    emp_data = records_list[0]
                    
                    st.subheader(f"👋 Welcome, {emp_data.get('Employee Name', 'Employee')}")
                    st.write(f"**Designation:** {emp_data.get('Designation', 'N/A')} | **Selected Month:** {selected_month}")
                    
                    st.markdown("---")
                    
                    # Generate text statement slip safely
                    slip_text = generate_text_slip(emp_data)
                    
                    # 📥 BIG BLUE SECURE STREAMLIT DOWNLOAD BUTTON
                    st.download_button(
                        label=f"📥 Click Here to Download PaySlip ({selected_month})",
                        data=slip_text,
                        file_name=f"PaySlip_{current_emp}_{selected_month}.txt",
                        mime="text/plain",
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
                        matches_list = emp_matches.to_dict(orient='records')
                        actual_old_pass = str(matches_list[0].get('Password', '')).strip()
                        
                        if current_password_input != actual_old_pass:
                            st.error("❌ Current Password galat hai! Kripya sahi password dalein.")
                        elif new_password_input != confirm_password_input:
                            st.error("❌ Naya password aur confirm password match nahi ho raha!")
                        elif len(new_password_input) < 4:
                            st.error("❌ Password kam se kam 4 aksharo ka hona chahiye.")
                        else:
                            df.loc[df['EmployeeCode'] == current_emp, 'Password'] = new_password_input
                            df.to_excel(excel_file, index=False)
                            st.success("✅ Password successfully update ho gaya hai!")
