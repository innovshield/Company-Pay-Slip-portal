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

# 📄 DYNAMIC HTML PAYSLIP GENERATION FUNCTION (All Components Statically Explicit)
def get_html_payslip(emp):
    # Function to safely pull float numbers from dict
    def get_val(key):
        try:
            val = emp.get(key)
            # If value is a series/array, pull first element
            if hasattr(val, 'values'):
                val = val.values[0]
            elif isinstance(val, list) or hasattr(val, '__values__'):
                val = val[0]
            return float(val)
        except:
            return 0.0

    # Function to safely format text outputs
    def fmt(val):
        v = get_val(val)
        return str(int(v)) if v > 0 else "-"

    # Dedicated deduction label check to match original blueprint filter
    def show_ded(label, key):
        v = get_val(key)
        return label if v > 0 else ""

    html_layout = f"""
    <div style="font-family: Arial, sans-serif; padding: 15px; border: 1px solid #CBD5E0; background-color: #FFF; border-radius: 8px;">
        <div style="text-align: center; margin-bottom: 15px;">
            <h2 style="color: #1A365D; margin: 0;">INNOVSHIELD MANAGEMENT PVT. LTD.</h2>
            <p style="color: #4A5568; margin: 3px 0; font-size: 13px;">Qutub Vihar, Dwarka, New Delhi</p>
            <h4 style="margin: 10px 0 0 0; color: #2D3748;">Pay Slip for the Month of: {emp.get('Month').values[0] if hasattr(emp.get('Month'), 'values') else emp.get('Month', 'N/A')}</h4>
        </div>
        <hr style="border: 0; border-top: 1px solid #E2E8F0; margin-bottom: 15px;"/>
        
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 15px;">
            <tr>
                <td style="padding: 6px;"><b>Emp Code:</b> {emp.get('EmployeeCode').values[0] if hasattr(emp.get('EmployeeCode'), 'values') else emp.get('EmployeeCode', '')}</td>
                <td style="padding: 6px;"><b>Name:</b> {emp.get('Employee Name').values[0] if hasattr(emp.get('Employee Name'), 'values') else emp.get('Employee Name', '')}</td>
                <td style="padding: 6px;"><b>Designation:</b> {emp.get('Designation').values[0] if hasattr(emp.get('Designation'), 'values') else emp.get('Designation', '')}</td>
            </tr>
            <tr>
                <td style="padding: 6px;"><b>Location:</b> {emp.get('Location').values[0] if hasattr(emp.get('Location'), 'values') else emp.get('Location', '')}</td>
                <td style="padding: 6px;"><b>A/c No:</b> {emp.get('Ac No').values[0] if hasattr(emp.get('Ac No'), 'values') else emp.get('Ac No', '')}</td>
                <td style="padding: 6px;"><b>UAN No:</b> {emp.get('UAN NO').values[0] if hasattr(emp.get('UAN NO'), 'values') else emp.get('UAN NO', '')}</td>
            </tr>
            <tr>
                <td style="padding: 6px;"><b>ESIC No:</b> {emp.get('ESIC NO').values[0] if hasattr(emp.get('ESIC NO'), 'values') else emp.get('ESIC NO', '')}</td>
                <td style="padding: 6px;"><b>Month Days:</b> {emp.get('Month Days').values[0] if hasattr(emp.get('Month Days'), 'values') else emp.get('Month Days', '')}</td>
                <td style="padding: 6px;"><b>Worked Days:</b> {emp.get('Worked Days').values[0] if hasattr(emp.get('Worked Days'), 'values') else emp.get('Worked Days', '')}</td>
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
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Basic Salary</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Fixed Basic')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Earn Basic')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">{show_ded('Provident Fund (PF)', 'PF')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('PF')}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">HRA</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Fixed HRA')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Earn HRA')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">{show_ded('ESIC', 'ESIC')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('ESIC')}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Statutory Bonus</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Fixed Stat Bonus')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Earn Stat Bon')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">{show_ded('LWF', 'LWF')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('LWF')}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Special Allowance</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Fixed Special')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Earn Special')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">{show_ded('EWF Deduc', 'EWF')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('EWF')}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Leave Encashment</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">-</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Leave Encash')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">{show_ded('Ship/COD Loss', 'Ship/COD Loss')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Ship/COD Loss')}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Attendance Bonus</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">-</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Atte Bonus')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">{show_ded('Salary Advance', 'Advance')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Advance')}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Mobile Allowance</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">-</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Mobile Allo')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">{show_ded('Notice Pay Deduct', 'Notice Pay')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Notice Pay')}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Special Incentive</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">-</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Special Incentive')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">-</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">-</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Group Incentive</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">-</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{fmt('Group Incentive')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">-</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">-</td>
            </tr>
            <tr>
