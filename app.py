import streamlit as st
import pandas as pd
from xhtml2pdf import pisa
import io

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Corporate PaySlip Portal", page_icon="🔒", layout="centered")

# INITIALIZE SESSION STATES
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'emp_code' not in st.session_state:
    st.session_state['emp_code'] = None

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

# SAFE NUMBER CONVERTER
def safe_num(val):
    try:
        if pd.isna(val) or val == "" or val == "-":
            return 0
        clean_val = str(val).replace('₹', '').replace('Rs.', '').replace(',', '').strip()
        return int(float(clean_val))
    except:
        return 0

# HTML GENERATOR (Used for both Screen rendering & PDF Generation)
def get_html_payslip(emp_data):
    fixed_gross = safe_num(emp_data.get('Fixed Gross', 0))
    total_earn = safe_num(emp_data.get('Total Earn', 0))
    total_dedu = safe_num(emp_data.get('Total Dedu', 0))
    net_pay = safe_num(emp_data.get('Net Pay', 0))
    
    other_inc = safe_num(emp_data.get('Arrears', 0)) + safe_num(emp_data.get('Incentive', 0)) + safe_num(emp_data.get('Performance', 0))
    mobile_and_incentives = safe_num(emp_data.get('Mobile Allo', 0)) + safe_num(emp_data.get('Special Incentive', 0)) + safe_num(emp_data.get('Group Incentive', 0)) + other_inc

    html_content = f"""
    <html>
    <head>
    <style>
        @page {{ size: A4; margin: 1cm; }}
        body {{ font-family: Helvetica, Arial, sans-serif; color: #333333; }}
        .container {{ border: 2px solid #1A365D; padding: 20px; border-radius: 8px; max-width: 650px; margin: auto; background-color: #ffffff; }}
        .header {{ text-align: center; margin-bottom: 20px; }}
        .title {{ color: #1A365D; margin: 0 0 5px 0; font-size: 20px; font-weight: bold; }}
        .subtitle {{ color: #4A5568; margin: 0; font-size: 11px; }}
        .slip-title {{ margin: 15px 0 0 0; color: #2B6CB0; text-decoration: underline; font-size: 14px; font-weight: bold; }}
        .info-table, .data-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 11px; }}
        .info-table td {{ padding: 6px; border: 1px solid #CBD5E0; background-color: #F7FAFC; }}
        .data-table th {{ background-color: #1A365D; color: white; font-weight: bold; text-align: center; padding: 8px; border: 1px solid #CBD5E0; }}
        .data-table td {{ padding: 6px; border: 1px solid #CBD5E0; text-align: center; }}
        .data-table .left-align {{ text-align: left; }}
        .total-row {{ background-color: #E2E8F0; font-weight: bold; }}
        .net-pay-box {{ background-color: #1A365D; color: white; padding: 10px; border-radius: 4px; text-align: center; font-size: 14px; font-weight: bold; margin-top: 15px; }}
        .footer {{ margin-top: 25px; font-size: 9px; color: #718096; text-align: center; border-top: 1px dashed #CBD5E0; padding-top: 10px; }}
    </style>
    </head>
    <body>
    <div class="container">
        <div class="header">
            <div class="title">YOUR COMPANY NAME PVT. LTD.</div>
            <div class="subtitle">Qutub Vihar, Dwarka, New Delhi</div>
            <div class="slip-title">Pay Slip for the Month of: {emp_data.get('Month', 'N/A')}</div>
        </div>
        
        <table class="info-table">
            <tr>
                <td><b>Emp Code:</b> {emp_data.get('EmployeeCode', '')}</td>
                <td><b>Name:</b> {emp_data.get('Employee Name', '')}</td>
                <td><b>Designation:</b> {emp_data.get('Designation', '')}</td>
            </tr>
            <tr>
                <td><b>Location:</b> {emp_data.get('Location', '')}</td>
                <td><b>A/c No:</b> {emp_data.get('Ac No', '')}</td>
                <td><b>UAN No:</b> {emp_data.get('UAN NO', '')}</td>
            </tr>
            <tr>
                <td><b>ESIC No:</b> {emp_data.get('ESIC NO', '')}</td>
                <td><b>Month Days:</b> {emp_data.get('Month Days', '')}</td>
                <td><b>Worked Days:</b> {emp_data.get('Worked Days', '')}</td>
            </tr>
        </table>
        
        <table class="data-table">
            <thead>
                <tr>
                    <th style="width: 35%;">Salary Component</th>
                    <th style="width: 15%;">Fixed Rate (₹)</th>
                    <th style="width: 15%;">Earned (₹)</th>
                    <th style="width: 20%;">Deductions</th>
                    <th style="width: 15%;">Amount (₹)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="left-align">Basic Salary</td>
                    <td>{safe_num(emp_data.get('Fixed Basic', 0))}</td>
                    <td>{safe_num(emp_data.get('Earn Basic', 0))}</td>
                    <td class="left-align">Provident Fund (PF)</td>
                    <td>{safe_num(emp_data.get('PF', 0))}</td>
                </tr>
                <tr>
                    <td class="left-align">HRA</td>
                    <td>{safe_num(emp_data.get('Fixed HRA', 0))}</td>
                    <td>{safe_num(emp_data.get('Earn HRA', 0))}</td>
                    <td class="left-align">ESIC</td>
                    <td>{safe_num(emp_data.get('ESIC', 0))}</td>
                </tr>
                <tr>
                    <td class="left-align">Statutory Bonus</td>
                    <td>{safe_num(emp_data.get('Fixed Stat Bonus', emp_data.get('Fixed Stat Bon', 0)))}</td>
                    <td>{safe_num(emp_data.get('Earn Stat Bon', emp_data.get('Earn Stat Bonus', 0)))}</td>
                    <td class="left-align">LWF</td>
                    <td>{safe_num(emp_data.get('LWF', 0))}</td>
                </tr>
                <tr>
                    <td class="left-align">Special Allowance</td>
                    <td>{safe_num(emp_data.get('Fixed Special', 0))}</td>
                    <td>{safe_num(emp_data.get('Earn Special', 0))}</td>
                    <td class="left-align">EWF Deduc</td>
                    <td>{safe_num(emp_data.get('EWF', 0))}</td>
                </tr>
                <tr>
                    <td class="left-align">Leave Encashment</td>
                    <td>-</td>
                    <td>{safe_num(emp_data.get('Leave Encash', 0))}</td>
                    <td class="left-align">Ship/COD Loss</td>
                    <td>{safe_num(emp_data.get('Ship/COD Loss', 0))}</td>
                </tr>
                <tr>
                    <td class="left-align">Attendance Bonus</td>
                    <td>-</td>
                    <td>{safe_num(emp_data.get('Atte Bonus', 0))}</td>
                    <td class="left-align">Salary Advance</td>
                    <td>{safe_num(emp_data.get('Advance', 0))}</td>
                </tr>
                <tr>
                    <td class="left-align">Mobile & Incentives</td>
                    <td>-</td>
                    <td>{mobile_and_incentives}</td>
                    <td class="left-align">Notice Pay Deduct</td>
                    <td>{safe_num(emp_data.get('Notice Pay', 0))}</td>
                </tr>
                <tr class="total-row">
                    <td class="left-align">Total Gross / Earnings</td>
                    <td>{fixed_gross}</td>
                    <td>{total_earn}</td>
                    <td class="left-align">Total Deductions</td>
                    <td>{total_dedu}</td>
                </tr>
            </tbody>
        </table>
        
        <div class="net-pay-box">
            NET TAKE HOME PAY: ₹{net_pay}/-
        </div>
        
        <div class="footer">
            *This is a computer-generated payslip and does not require a physical signature.
        </div>
    </div>
    </body>
    </html>
    """
    return html_content

# ENGINE TO TRANSLATE HTML STRING INTO PDF BYTES
def convert_html_to_pdf(html_string):
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html_string), dest=pdf_buffer)
    if pisa_status.err:
        return None
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# --- INTERFACE ROUTING ---
if not st.session_state['logged_in']:
    st.title("🔒 Corporate PaySlip Portal")
    login_tab, admin_tab = st.tabs(["👤 Employee Login", "🛠️ Admin Portal"])
    
    with login_tab:
        # Use formal Streamlit form context so submit button renders properly
        with st.form(key="employee_login_form"):
            st.subheader("Employee Sign-In")
            emp_code = st.text_input("Employee Code", placeholder="e.g., EMP001").strip()
            emp_mob = st.text_input("Registered Mobile / Password", type="password").strip()
            submit_employee = st.form_submit_button(label="Submit Details & Login")
            
            if submit_employee:
                if emp_code and emp_mob:
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = 'employee'
                    st.session_state['emp_code'] = emp_code
                    st.rerun()
                else:
                    st.error("Please fill out all the input fields before submitting.")
                
    with admin_tab:
        with st.form(key="admin_login_form"):
            st.subheader("Admin Portal Access")
            admin_username = st.text_input("Admin Username")
            admin_password = st.text_input("Admin Password", type="password")
            submit_admin = st.form_submit_button(label="Verify Credentials")
            
            if submit_admin:
                if admin_username == ADMIN_USER and admin_password == ADMIN_PASS:
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = 'admin'
                    st.rerun()
                else:
