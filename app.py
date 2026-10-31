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
            
            # String cleaning to handle type comparison without conversion crashes
            df['EmployeeCode'] = df['EmployeeCode'].astype(str).str.strip()
            df['Password'] = df['Password'].astype(str).str.strip()
            
            # Match current valid target user entry row
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

# 📄 SAFE FUNCTION TO GENERATE COMPLETE PAYSLIP STRUCTURE
def get_html_payslip(emp):
    # Safe float fallback evaluator helper lambda
    safe_val = lambda key: int(float(emp.get(key, 0))) if emp.get(key) and str(emp.get(key)).strip().lower() != 'none' and str(emp.get(key)).strip() != '' else 0

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
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Fixed Basic')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Earn Basic')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Provident Fund (PF)</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('PF')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">HRA</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Fixed HRA')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Earn HRA')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">ESIC</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('ESIC')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Statutory Bonus</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Fixed Stat Bonus')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Earn Stat Bon')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">LWF</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('LWF')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Special Allowance</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Fixed Special')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Earn Special')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">EWF Deduc</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('EWF')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Leave Encashment</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Leave Encash')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Ship/COD Loss</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Ship/COD Loss')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Attendance Bonus</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Atte Bonus')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Salary Advance</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Advance')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Mobile Allowances</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Mobile Allo')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Notice Pay Deduct</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Notice Pay')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Group Incentive</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Group Incentive')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Other Deductions</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Other Deduc')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Arrears / Other</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Arrears')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">-</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">0</td>
            </tr>
            <tr style="background-color: #EDF2F7; font-weight: bold;">
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Gross Total</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Gross Fixed')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Gross Earned')}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Total Deductions</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">{safe_val('Total Deduc')}</td>
            </tr>
        </table>
        <div style="margin-top: 15px; padding: 10px; background-color: #EBF8FF; border-left: 4px solid #3182CE; font-weight: bold; font-size: 14px;">
