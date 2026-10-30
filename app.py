import sys
import subprocess

# 🌟 AUTOMATIC DEPENDENCY CHECKER (Bina requirements file ke automatic installation)
try:
    import openpyxl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])

import streamlit as st
import pandas as pd

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Corporate PaySlip Portal", page_icon="🔒", layout="centered")
st.title("🔒 Secure Corporate PaySlip Portal")

# SAFE NUMBER CONVERTER (Bina crash hue safe data nikalne ke liye)
def safe_num(val):
    try:
        if pd.isna(val) or val == "" or val == "-":
            return 0
        clean_val = str(val).replace('₹', '').replace('Rs.', '').replace(',', '').strip()
        return int(float(clean_val))
    except:
        return 0

# 2. FUNCTION TO GENERATE PROFESSIONAL HTML-BASED PRINTABLE PAYSLIP
def get_html_payslip(emp_data):
    fixed_gross = safe_num(emp_data.get('Fixed Gross', 0))
    total_earn = safe_num(emp_data.get('Total Earn', 0))
    total_dedu = safe_num(emp_data.get('Total Dedu', 0))
    net_pay = safe_num(emp_data.get('Net Pay', 0))
    
    other_inc = safe_num(emp_data.get('Arrears', 0)) + safe_num(emp_data.get('Incentive', 0)) + safe_num(emp_data.get('Performance', 0))
    mobile_and_incentives = safe_num(emp_data.get('Mobile Allo', 0)) + safe_num(emp_data.get('Special Incentive', 0)) + safe_num(emp_data.get('Group Incentive', 0)) + other_inc

    html_content = f"""
    <div style="font-family: Arial, sans-serif; border: 2px solid #1A365D; padding: 20px; border-radius: 8px; max-width: 650px; margin: auto; background-color: #ffffff; color: #333333;">
        <!-- Header -->
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #1A365D; margin: 0 0 5px 0; font-size: 22px;">YOUR COMPANY NAME PVT. LTD.</h2>
            <p style="color: #4A5568; margin: 0; font-size: 12px;">Qutub Vihar, Dwarka, New Delhi</p>
            <h4 style="margin: 15px 0 0 0; color: #2B6CB0; text-decoration: underline;">Pay Slip for the Month of: {emp_data.get('Month', 'N/A')}</h4>
        </div>
        
        <!-- Employee Master Details Table -->
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 12px;">
            <tr style="background-color: #F7FAFC;">
                <td style="padding: 6px; border: 1px solid #CBD5E0;"><b>Emp Code:</b> {emp_data.get('EmployeeCode', '')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;"><b>Name:</b> {emp_data.get('Employee Name', '')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;"><b>Designation:</b> {emp_data.get('Designation', '')}</td>
            </tr>
            <tr style="background-color: #F7FAFC;">
                <td style="padding: 6px; border: 1px solid #CBD5E0;"><b>Location:</b> {emp_data.get('Location', '')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;"><b>A/c No:</b> {emp_data.get('Ac No', '')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;"><b>UAN No:</b> {emp_data.get('UAN NO', '')}</td>
            </tr>
            <tr style="background-color: #F7FAFC;">
                <td style="padding: 6px; border: 1px solid #CBD5E0;"><b>ESIC No:</b> {emp_data.get('ESIC NO', '')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;"><b>Month Days:</b> {emp_data.get('Month Days', '')}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;"><b>Worked Days:</b> {emp_data.get('Worked Days', '')}</td>
            </tr>
        </table>
        
        <!-- Salary Breakdown Structure -->
        <table style="width: 100%; border-collapse: collapse; font-size: 11px; margin-bottom: 20px;">
            <tr style="background-color: #1A365D; color: white; font-weight: bold; text-align: center;">
                <td style="padding: 8px; border: 1px solid #CBD5E0; width: 35%;">Salary Component</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0; width: 15%;">Fixed Rate (₹)</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0; width: 15%;">Earned (₹)</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0; width: 20%;">Deductions</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0; width: 15%;">Amount (₹)</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Basic Salary</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('Fixed Basic', 0))}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('Earn Basic', 0))}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Provident Fund (PF)</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('PF', 0))}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">HRA</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('Fixed HRA', 0))}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('Earn HRA', 0))}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">ESIC</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('ESIC', 0))}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Statutory Bonus</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('Fixed Stat Bonus', emp_data.get('Fixed Stat Bon', 0)))}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('Earn Stat Bon', emp_data.get('Earn Stat Bonus', 0)))}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">LWF</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('LWF', 0))}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Special Allowance</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('Fixed Special', 0))}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('Earn Special', 0))}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">EWF Deduc</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('EWF', 0))}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Leave Encashment</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">-</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('Leave Encash', 0))}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Ship/COD Loss</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('Ship/COD Loss', 0))}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Attendance Bonus</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">-</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('Atte Bonus', 0))}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Salary Advance</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('Advance', 0))}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Mobile & Incentives</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">-</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{mobile_and_incentives}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0;">Notice Pay Deduct</td>
                <td style="padding: 6px; border: 1px solid #CBD5E0; text-align: center;">{safe_num(emp_data.get('Notice Pay', 0))}</td>
            </tr>
            <tr style="background-color: #F7FAFC; font-weight: bold;">
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Gross Totals</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0; text-align: center;">{fixed_gross}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0; text-align: center;">{total_earn}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0;">Total Deduction</td>
                <td style="padding: 8px; border: 1px solid #CBD5E0; text-align: center;">{total_dedu}</td>
            </tr>
            <tr style="background-color: #EBF8FF; font-weight: bold; font-size: 13px; color: #2B6CB0;">
                <td colspan="3" style="padding: 10px; border: 1px solid #CBD5E0;">NET PAYABLE TAKE-HOME SALARY</td>
                <td colspan="2" style="padding: 10px; border: 1px solid #CBD5E0; text-align: center; font-size: 15px;">₹{net_pay}</td>
            </tr>
        </table>
        
        <p style="font-size: 10px; color: #718096; text-align: center; margin-top: 15px; font-style: italic;">Note: This is a system-generated secure digital payslip and does not require a physical signature or stamp.</p>
    </div>
    """
    return html_content

# 3. APPLICATION STARTPOINT
