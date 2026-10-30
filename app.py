import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import os

# 1. 🔒 PAGE CONFIG & EXPERT SECURITY LAYOUT LOCK
st.set_page_config(page_title="Corporate PaySlip Portal", page_icon="🔒", layout="centered")

# Hardening UI: Hides Main Menu, Footers, Headers, Deploy buttons, and Source Viewer completely
st.markdown("""
    <style>
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stAppDeployButton {display: none !important;}
    button[title="View source code"] {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    </style>
    """, unsafe_allow_html=True)

# 2. 🔑 MOCK DATA & SESSION STATE DATABASE (For Validation & Live Updates)
if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "IS-10245": {
            "name": "Rahul Sharma", "password": "password123", "dept": "Engineering", 
            "desig": "Senior Software Engineer", "bank": "XXXXXX12345", "pan": "ABCDE1234F", 
            "basic": 50000, "hra": 20000, "special": 15000, "pf": 1800, "pt": 200, "tds": 5000
        }
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# 📄 DYNAMIC PDF GENERATION FUNCTION (ReportLab Powered)
def generate_pdf(emp_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, spaceAfter=2, textColor=colors.HexColor("#1A365D"), fontSize=18)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], alignment=1, spaceAfter=12, textColor=colors.HexColor("#4A5568"), fontSize=9)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=8, leading=10)
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10)
    header_text_style = ParagraphStyle('HeaderTextStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)
    
    # Corporate Branding Headers
    story.append(Paragraph("<b>INNOVSHIELD MANAGEMENT PVT. LTD.</b>", title_style))
    story.append(Paragraph("Qutub Vihar, Dwarka, New Delhi", subtitle_style))
    story.append(Paragraph(f"<b>Pay Slip for the Month of:</b> {emp_data.get('Month', 'N/A')}", ParagraphStyle('H3', parent=styles['Heading3'], alignment=1, spaceAfter=10)))
    story.append(Spacer(1, 5))
    
    # Employee Master Profile Information Block (Fixed Widths)
    info_data = [
        [Paragraph(f"<b>Emp Code:</b> {emp_data.get('EmployeeCode', '')}", normal_style), Paragraph(f"<b>Name:</b> {emp_data.get('Employee Name', '')}", normal_style)],
        [Paragraph(f"<b>Department:</b> {emp_data.get('Department', '')}", normal_style), Paragraph(f"<b>Designation:</b> {emp_data.get('Designation', '')}", normal_style)],
        [Paragraph(f"<b>Bank A/C No:</b> {emp_data.get('BankAccount', '')}", normal_style), Paragraph(f"<b>PAN:</b> {emp_data.get('PAN', '')}", normal_style)]
    ]
    
    info_table = Table(info_data, colWidths=[270, 270])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))
    
    # Financial breakdown matrices
    breakdown_headers = [
        [Paragraph("Earnings Breakdown", header_text_style), Paragraph("Amount (INR)", header_text_style),
         Paragraph("Deductions Breakdown", header_text_style), Paragraph("Amount (INR)", header_text_style)]
    ]
    
    breakdown_data = [
        [Paragraph("Basic Salary", normal_style), Paragraph(f"{emp_data.get('Basic', 0):,.2f}", normal_style),
         Paragraph("Provident Fund (PF)", normal_style), Paragraph(f"{emp_data.get('PF', 0):,.2f}", normal_style)],
        [Paragraph("House Rent Allowance (HRA)", normal_style), Paragraph(f"{emp_data.get('HRA', 0):,.2f}", normal_style),
         Paragraph("Professional Tax (PT)", normal_style), Paragraph(f"{emp_data.get('PT', 0):,.2f}", normal_style)],
        [Paragraph("Special Allowance", normal_style), Paragraph(f"{emp_data.get('SpecialAllowance', 0):,.2f}", normal_style),
         Paragraph("Income Tax (TDS)", normal_style), Paragraph(f"{emp_data.get('TDS', 0):,.2f}", normal_style)],
        [Paragraph("<b>Total Earnings</b>", bold_style), Paragraph(f"<b>{emp_data.get('TotalEarnings', 0):,.2f}</b>", bold_style),
         Paragraph("<b>Total Deductions</b>", bold_style), Paragraph(f"<b>{emp_data.get('TotalDeductions', 0):,.2f}</b>", bold_style)]
    ]
    
    financial_table = Table(breakdown_headers + breakdown_data, colWidths=[160, 110, 160, 110])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#EDF2F7")),
    ]))
    story.append(financial_table)
    story.append(Spacer(1, 15))
    
    # Net Pay Frame Block
    net_pay = emp_data.get('TotalEarnings', 0) - emp_data.get('TotalDeductions', 0)
    net_pay_data = [
        [Paragraph(f"<b>NET TAKE-HOME PAY:</b>", bold_style), Paragraph(f"<b>INR {net_pay:,.2f}</b>", ParagraphStyle('NetPay', parent=bold_style, fontSize=10, textColor=colors.HexColor("#2F855A")))]
    ]
    net_pay_table = Table(net_pay_data, colWidths=[200, 340])
    net_pay_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E6FFFA")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#319795")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(net_pay_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# 3. 🛡️ VIEW LOGIC CONSTRAINTS
if not st.session_state.logged_in:
    st.title("🔒 Secure Corporate PaySlip Portal")
    st.subheader("Employee Portal Entry")
    
    with st.form("secure_login"):
        user_input = st.text_input("Employee Code (e.g. IS-10245)").strip()
        pass_input = st.text_input("Secure Password", type="password")
        login_btn = st.form_submit_button("Sign In")
        
        if login_btn:
            if user_input in st.session_state.user_db and st.session_state.user_db[user_input]["password"] == pass_input:
                st.session_state.logged_in = True
                st.session_state.current_user = user_input
                st.rerun()
            else:
                st.error("Authentication failed. Check your Code or Password.")

else:
    # Authenticated State User References
    current_emp = st.session_state.current_user
    db_profile = st.session_state.user_db[current_emp]
    
    st.title("🔒 Secure Corporate PaySlip Portal")
    
    # 🎛️ SIDEBAR NAVIGATION (Protected Context Only)
    st.sidebar.title(f"👤 {db_profile['name']}")
    st.sidebar.write(f"**ID:** {current_emp}")
    
    app_mode = st.sidebar.radio("Dashboard Action", ["Download PaySlip", "Account Security Settings"])
    
    if st.sidebar.button("🚪 Terminate Session (Logout)"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()
        
    # MAIN APPLICATION LOGIC FLOW
    if app_mode == "Download PaySlip":
        st.subheader("📋 Your Verified Payroll Ledger")
        month_choice = st.selectbox("Select Target Roster Month", ["October 2026", "November 2026", "December 2026"])
        
        # Calculate totals dynamically based on profile variables securely
        total_e = db_profile['basic'] + db_profile['hra'] + db_profile['special']
        total_d = db_profile['pf'] + db_profile['pt'] + db_profile['tds']
        
        secure_bundle = {
            "EmployeeCode": current_emp, "Employee Name": db_profile['name'],
            "Department": db_profile['dept'], "Designation": db_profile['desig'],
            "Month": month_choice, "BankAccount": db_profile['bank'], "PAN": db_profile['pan'],
            "Basic": db_profile['basic'], "HRA": db_profile['hra'], "SpecialAllowance": db_profile['special'],
            "PF": db_profile['pf'], "PT": db_profile['pt'], "TDS": db_profile['tds'],
            "TotalEarnings": total_e, "TotalDeductions": total_d
        }
        
        if st.button("✨ Compile & Generate Secure PDF"):
            pdf_data = generate_pdf(secure_bundle)
            st.success("PaySlip compiled successfully in target session memory!")
            
            st.download_button(
                label="📥 Download Official PaySlip PDF",
                data=pdf_data,
                file_name=f"PaySlip_{current_emp}_{month_choice.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
            
    elif app_mode == "Account Security Settings":
        st.subheader("🔑 Change System Access Password")
        
        with st.form("password_mutation"):
            old_p = st.text_input("Current System Password", type="password")
            new_p = st.text_input("New Identity Password", type="password")
            confirm_p = st.text_input("Confirm New Password", type="password")
            update_btn = st.form_submit_button("Update Credentials")
            
            if update_btn:
