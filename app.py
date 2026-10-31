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

# 🔄 SAFE DATABASE RE-WRITE LOGIC FOR PASSWORD RESET
def reset_excel_password(emp_code, current_password, new_password):
    try:
        if os.path.exists(excel_file):
            df = pd.read_excel(excel_file)
            
            df['EmployeeCode'] = df['EmployeeCode'].astype(str).str.strip()
            df['Password'] = df['Password'].astype(str).str.strip()
            
            target_mask = (df['EmployeeCode'] == str(emp_code).strip()) & (df['Password'] == str(current_password).strip())
            matched_indices = df[target_mask].index
            
            if not matched_indices.empty:
                df.loc[matched_indices, 'Password'] = str(new_password).strip()
                df.to_excel(excel_file, index=False)
                return True, "🎉 Password updated successfully! You can now log in."
            else:
                return False, "❌ Invalid Employee Code or Current Password."
        else:
            return False, "⚠️ System Error: database file 'salary_data.xlsx' not found."
    except Exception as e:
        return False, f"⚠️ Database Modification Failure: {str(e)}"

# Helper function to clean values safely outside the f-string layout
def clean_val(emp, key):
    val = emp.get(key, 0)
    if pd.isna(val) or str(val).strip().lower() == 'none' or str(val).strip() == '':
        return 0
    try:
        return int(float(val))
    except:
        return 0

# 📄 SAFE FUNCTION TO GENERATE COMPLETE PAYSLIP STRUCTURE
def get_html_payslip(emp):
    # Fetch data into local clean variables to avoid f-string bracket collapse
    m_days = emp.get('Month Days', '')
    w_days = emp.get('Worked Days', '')
    fixed_b = clean_val(emp, 'Fixed Basic')
    earn_b = clean_val(emp, 'Earn Basic')
    pf_v = clean_val(emp, 'PF')
    fixed_h = clean_val(emp, 'Fixed HRA')
    earn_h = clean_val(emp, 'Earn HRA')
    esic_v = clean_val(emp, 'ESIC')
    fixed_sb = clean_val(emp, 'Fixed Stat Bonus')
    earn_sb = clean_val(emp, 'Earn Stat Bon')
    lwf_v = clean_val(emp, 'LWF')
    fixed_sp = clean_val(emp, 'Fixed Special')
    earn_sp = clean_val(emp, 'Earn Special')
    ewf_v = clean_val(emp, 'EWF')
    leave_v = clean_val(emp, 'Leave Encash')
    ship_v = clean_val(emp, 'Ship/COD Loss')
    atte_v = clean_val(emp, 'Atte Bonus')
    adv_v = clean_val(emp, 'Advance')
    mob_v = clean_val(emp, 'Mobile Allo')
    notice_v = clean_val(emp, 'Notice Pay')
    group_v = clean_val(emp, 'Group Incentive')
    other_v = clean_val(emp, 'Other Deduc')
    arr_v = clean_val(emp, 'Arrears')
    g_fixed = clean_val(emp, 'Gross Fixed')
    g_earn = clean_val(emp, 'Gross Earned')
    t_deduc = clean_val(emp, 'Total Deduc')
    net_p = clean_val(emp, 'Net Payable')

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
                <td style="padding: 6px;"><b>Month Days:</b> {m_days}</td>
                <td style="padding: 6px;"><b>Worked Days:</b> {w_days}</td>
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
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{fixed_b}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{earn_b}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Provident Fund (PF)</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{pf_v}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">HRA</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{fixed_h}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{earn_h}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">ESIC</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{esic_v}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Statutory Bonus</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{fixed_sb}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{earn_sb}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">LWF</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{lwf_v}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Special Allowance</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{fixed_sp}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{earn_sp}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">EWF Deduc</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{ewf_v}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Leave Encashment</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{leave_v}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Ship/COD Loss</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{ship_v}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Attendance Bonus</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{atte_v}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Salary Advance</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{adv_v}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Mobile Allowances</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{mob_v}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Notice Pay Deduct</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{notice_v}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Group Incentive</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{group_v}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Other Deductions</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{other_v}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Arrears / Other</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{arr_v}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">-</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
            </tr>
