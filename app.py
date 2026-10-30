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
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('None', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Leave Encash', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Ship/COD Loss</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Ship/COD Loss', 0)))}</td>
            </tr>
	    <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Attendance Bonus</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('None', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Atte Bonus', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Salary Advance</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Advance', 0)))}</td>
            </tr>
	    <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Mobile Allowances</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('None', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Mobile Allo', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Notice Pay Deduct</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Notice Pay', 0)))}</td>
            </tr>
	    <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Group Incentive</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('None', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Group Incentive', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('None', 0)))}</td>
            </tr>
	    <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Arrears / Other</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('None', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Arrears', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('None', 0)))}</td>
            </tr>
	    <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Incentive / Performance</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('None', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Incentive', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('None', 0)))}</td>
            </tr>
            <tr style="background-color: #F7FAFC; font-weight: bold;">
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Gross Total</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Fixed Gross', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Total Earn', 0)))}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Total Deduction</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{int(float(emp.get('Total Dedu', 0)))}</td>
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

    # GATEKEEPER MODE
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
        # SECURE DASHBOARD VIEWPORT
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
                    # Clean dictionary conversion to avoid structural list mismatch
                    emp_data_list = target_df.to_dict(orient='records')
                    emp_data = emp_data_list[0]
                    
                    st.subheader(f"👋 Welcome, {emp_data.get('Employee Name', 'Employee')}")
                    st.write(f"**Designation:** {emp_data.get('Designation', 'N/A')} | **Selected Month:** {selected_month}")
                    
                    st.markdown("---")
                    
                    # Renders beautiful live preview on screen
                    payslip_html = get_html_payslip(emp_data)
                    st.markdown(payslip_html, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # 📥 MULTI-DEVICE SUPPORTED SECURE PDF DOWNLOAD ACTION BUTTON
                    st.download_button(
                        label=f"📥 Click Here to Download PaySlip ({selected_month}) - PDF format",
                        data=payslip_html,
                        file_name=f"PaySlip_{current_emp}_{selected_month}.html",
                        mime="text/html",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Selected month ka data nahi mila.")
            else:
                st.error("❌ Employee records database matching error.")
                
        with tab2:
            st.subheader("🛠️ Account Security Settings")
            st.write("Aap yahan se apna login password secure tarike se change kar sakte hain:")
            
            with st.form("change_password_form"):
                current_password_input = st.text_input("Current Password:", type="password").strip()
