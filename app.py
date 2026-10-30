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

# 🛠️ HELPER: MOCK DATA CREATOR (Fixed Syntax Error here)
def create_mock_data():
    if not os.path.exists(excel_file):
        mock_df = pd.DataFrame({
            'EmployeeCode': ['EMP001', 'EMP002'],
            'Password': ['pass123', 'secure456'],
            'Employee Name': ['Amit Sharma', 'Priya Patel'],
            'Designation': ['Software Engineer', 'HR Manager'],
            'Month': ['October 2026', 'October 2026'],
            'Basic':,
            'HRA':,                 # Test case: 0 value will be hidden automatically
            'Special Allowance':,    # Test case: 0 value will be hidden automatically
            'Deductions':,
            'PF': [1800, 0]                    # Test case: 0 value will be hidden automatically
        })
        mock_df.to_excel(excel_file, index=False)

create_mock_data()

# 📄 SAFE FUNCTION TO GENERATE COMPLETE PAYSLIP STRUCTURE (DYNAMIC ROWS)
def get_html_payslip(emp):
    earning_keys = ['Basic', 'HRA', 'Special Allowance', 'Dearness Allowance', 'Medical Allowance']
    deduction_keys = ['Deductions', 'PF', 'Professional Tax', 'TDS']
    
    # Clean and filter out keys with 0, empty string, or Null values dynamically
    active_earnings = {}
    for k in earning_keys:
        val = emp.get(k)
        if pd.notna(val) and val != "":
            try:
                float_val = float(val)
                if float_val > 0:
                    active_earnings[k] = float_val
            except ValueError:
                pass

    active_deductions = {}
    for k in deduction_keys:
        val = emp.get(k)
        if pd.notna(val) and val != "":
            try:
                float_val = float(val)
                if float_val > 0:
                    active_deductions[k] = float_val
            except ValueError:
                pass
    
    total_earnings = sum(active_earnings.values())
    total_deductions = sum(active_deductions.values())
    net_salary = total_earnings - total_deductions

    earn_items = list(active_earnings.items())
    deduct_items = list(active_deductions.items())
    max_rows = max(len(earn_items), len(deduct_items))
    
    table_rows_html = ""
    for i in range(max_rows):
        if i < len(earn_items):
            e_name, e_val = earn_items[i]
            earn_td = f"<td style='padding: 8px;'>{e_name}</td><td style='padding: 8px; text-align: right;'>{e_val:,.2f}</td>"
        else:
            earn_td = "<td style='padding: 8px;'></td><td style='padding: 8px; text-align: right;'></td>"
            
        if i < len(deduct_items):
            d_name, d_val = deduct_items[i]
            deduct_td = f"<td style='padding: 8px;'>{d_name}</td><td style='padding: 8px; text-align: right;'>{d_val:,.2f}</td>"
        else:
            deduct_td = "<td style='padding: 8px;'></td><td style='padding: 8px; text-align: right;'></td>"
            
        table_rows_html += f"<tr style='border-bottom: 1px solid #E2E8F0;'>{earn_td}{deduct_td}</tr>"

    html_layout = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #CBD5E0; background-color: #FFF; border-radius: 8px;">
        <div style="text-align: center; margin-bottom: 15px;">
            <h2 style="color: #1A365D; margin: 0;">INNOVSHIELD MANAGEMENT PVT. LTD.</h2>
            <p style="color: #4A5568; margin: 3px 0; font-size: 13px;">Qutub Vihar, Dwarka, New Delhi</p>
            <h4 style="margin: 10px 0 0 0; color: #2D3748;">Pay Slip for the Month of: {emp.get('Month', 'N/A')}</h4>
        </div>
        <hr style="border: 0; border-top: 1px solid #E2E8F0; margin-bottom: 15px;"/>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 15px;">
            <tr>
                <td style="padding: 6px; width: 33%;"><b>Emp Code:</b> {emp.get('EmployeeCode', '')}</td>
                <td style="padding: 6px; width: 33%;"><b>Name:</b> {emp.get('Employee Name', '')}</td>
                <td style="padding: 6px; width: 33%;"><b>Designation:</b> {emp.get('Designation', '')}</td>
            </tr>
        </table>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; border: 1px solid #E2E8F0;">
            <tr style="background-color: #F7FAFC; border-bottom: 1px solid #E2E8F0;">
                <th style="padding: 8px; text-align: left; width: 35%;">Earnings</th>
                <th style="padding: 8px; text-align: right; width: 15%;">Amount (₹)</th>
                <th style="padding: 8px; text-align: left; width: 35%;">Deductions</th>
                <th style="padding: 8px; text-align: right; width: 15%;">Amount (₹)</th>
            </tr>
            {table_rows_html}
            <tr style="background-color: #EDF2F7; font-weight: bold;">
                <td style="padding: 8px;">Gross Earnings</td>
                <td style="padding: 8px; text-align: right;">{total_earnings:,.2f}</td>
                <td style="padding: 8px;">Total Deductions</td>
                <td style="padding: 8px; text-align: right;">{total_deductions:,.2f}</td>
            </tr>
        </table>
        <div style="margin-top: 15px; padding: 10px; background-color: #EBF8FF; border-radius: 4px; text-align: right; font-size: 14px; font-weight: bold; color: #2B6CB0;">
            Net Salary Payable: ₹{net_salary:,.2f}
        </div>
    </div>
    """
    return html_layout

# 2. APPLICATION ROUTING (LOGIN VS DASHBOARD)
if not st.session_state['is_authenticated']:
    st.subheader("🔑 Employee Self-Service Portal")
    
    with st.form("login_form"):
        emp_code = st.text_input("Employee Code").strip()
        password = st.text_input("Password", type="password").strip()
        submit_button = st.form_submit_button("Access Portal")
        
        if submit_button:
            if os.path.exists(excel_file):
                try:
                    df = pd.read_excel(excel_file)
                    df.columns = df.columns.str.strip()
                    
                    # Convert match lookup columns cleanly into string type
                    df['EmployeeCode'] = df['EmployeeCode'].astype(str).str.strip()
                    df['Password'] = df['Password'].astype(str).str.strip()
                    
                    match = df[(df['EmployeeCode'] == emp_code) & (df['Password'] == password)]
                    
                    if not match.empty:
                        st.session_state['is_authenticated'] = True
                        # Select first row match record cleanly
                        st.session_state['logged_in_user'] = match.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("Invalid Employee Code or Password.")
                except Exception as e:
                    st.error(f"Error loading system database: {e}")
            else:
                st.error("Database file missing. Please contact HR.")
else:
    # 3. SECURE PAYSLIP DASHBOARD
    user_data = st.session_state['logged_in_user']
    
    col1, col2 = st.columns()
    with col1:
        st.success(f"Welcome, {user_data.get('Employee Name', 'User')}")
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state['is_authenticated'] = False
            st.session_state['logged_in_user'] = None
            st.rerun()
            
    st.write("### Your Digital Pay Slip")
    
    payslip_html = get_html_payslip(user_data)
    st.markdown(payslip_html, unsafe_allow_html=True)
    
    st.caption("To save as a PDF, press **Ctrl+P** (or **Cmd+P** on Mac) to open the browser print menu.")
