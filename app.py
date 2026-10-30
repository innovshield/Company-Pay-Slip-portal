import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# 🔒 PAGE CONFIG & SECURITY SETUP
st.set_page_config(page_title="Corporate PaySlip Portal", page_icon="🔒", layout="centered")

# Mock Database: Real-world mein ye database ya encrypted file se connect hoga
if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "IS-10245": {"name": "Rahul Sharma", "password": "password123", "dept": "Engineering", "desig": "Senior Software Engineer", "bank": "XXXXXX12345", "pan": "ABCDE1234F", "basic": 50000, "hra": 20000, "special": 15000, "pf": 1800, "pt": 200, "tds": 5000},
        "IS-10246": {"name": "Amit Kumar", "password": "secure456", "dept": "Operations", "desig": "Operations Manager", "bank": "XXXXXX67890", "pan": "XYZWR5678G", "basic": 45000, "hra": 18000, "special": 12000, "pf": 1800, "pt": 200, "tds": 4000}
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# 📄 DYNAMIC PDF GENERATION FUNCTION
def generate_pdf(emp_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30, title="Pay Slip")
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, spaceAfter=2, textColor=colors.HexColor("#1A365D"), fontSize=18)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], alignment=1, spaceAfter=12, textColor=colors.HexColor("#4A5568"), fontSize=9)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=8, leading=10)
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10)
    header_text_style = ParagraphStyle('HeaderTextStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)
    
    story.append(Paragraph("<b>INNOVSHIELD MANAGEMENT PVT. LTD.</b>", title_style))
    story.append(Paragraph("Qutub Vihar, Dwarka, New Delhi", subtitle_style))
    story.append(Paragraph(f"<b>Pay Slip for the Month of:</b> {emp_data.get('Month', 'N/A')}", ParagraphStyle('H3', parent=styles['Heading3'], alignment=1, spaceAfter=10)))
    story.append(Spacer(1, 5))
    
    info_data = [
        [Paragraph(f"<b>Emp Code:</b> {emp_data.get('EmployeeCode', '')}", normal_style), Paragraph(f"<b>Name:</b> {emp_data.get('Employee Name', '')}", normal_style)],
        [Paragraph(f"<b>Department:</b> {emp_data.get('Department', '')}", normal_style), Paragraph(f"<b>Designation:</b> {emp_data.get('Designation', '')}", normal_style)],
        [Paragraph(f"<b>Bank A/C No:</b> {emp_data.get('BankAccount', '')}", normal_style), Paragraph(f"<b>PAN:</b> {emp_data.get('PAN', '')}", normal_style)]
    ]
    
    info_table = Table(info_data, colWidths=[260, 260])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))
    
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
    
    financial_table = Table(breakdown_headers + breakdown_data, colWidths=[160, 100, 160, 100])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#EDF2F7")),
    ]))
    story.append(financial_table)
    story.append(Spacer(1, 15))
    
    net_pay = emp_data.get('TotalEarnings', 0) - emp_data.get('TotalDeductions', 0)
    net_pay_data = [
        [Paragraph(f"<b>NET TAKE-HOME PAY:</b>", bold_style), Paragraph(f"<b>INR {net_pay:,.2f}</b>", ParagraphStyle('NetPay', parent=bold_style, fontSize=10, textColor=colors.HexColor("#2F855A")))]
    ]
    net_pay_table = Table(net_pay_data, colWidths=[150, 370])
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


# 🔑 LOGIN INTERFACE
if not st.session_state.logged_in:
    st.subheader("🔒 Employee Secure Sign-In")
    
    with st.form("login_form"):
        input_user = st.text_input("Employee Code (e.g., IS-10245)").strip()
        input_pass = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button("Login")
        
        if submit_btn:
            if input_user in st.session_state.user_db and st.session_state.user_db[input_user]["password"] == input_pass:
                st.session_state.logged_in = True
                st.session_state.current_user = input_user
                st.rerun()
            else:
                st.error("Invalid Employee Code or Password. Please try again.")

# 🎯 SECURE DASHBOARD (Only visible after login)
else:
    emp_code = st.session_state.current_user
    user_info = st.session_state.user_db[emp_code]
    
    # Sidebar Navigation & Management
    st.sidebar.title(f"Welcome, {user_info['name']}")
    st.sidebar.write(f"**Emp Code:** {emp_code}")
    
    menu = st.sidebar.radio("Navigation", ["Download PaySlip", "Change Password"])
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    # SECTION 1: DOWNLOAD PAYSLIP
    if menu == "Download PaySlip":
        st.subheader("📋 Your Digital PaySlip Dashboard")
        
        selected_month = st.selectbox("Select PaySlip Month", ["October 2026", "November 2026", "December 2026"])
        
        # Calculate totals dynamically based on secure DB data
        total_earnings = user_info['basic'] + user_info['hra'] + user_info['special']
        total_deductions = user_info['pf'] + user_info['pt'] + user_info['tds']
        
        # Compile secure employee object
        secure_emp_data = {
            "EmployeeCode": emp_code,
            "Employee Name": user_info['name'],
            "Department": user_info['dept'],
            "Designation": user_info['desig'],
            "Month": selected_month,
            "BankAccount": user_info['bank'],
            "PAN": user_info['pan'],
            "Basic": user_info['basic'],
            "HRA": user_info['hra'],
            "SpecialAllowance": user_info['special'],
            "PF": user_info['pf'],
            "PT": user_info['pt'],
            "TDS": user_info['tds'],
            "TotalEarnings": total_earnings,
            "TotalDeductions": total_deductions
        }
        
        st.info("Your salary details are safely verified via tokenized secure session.")
        
        if st.button("✨ Compile & Verify PaySlip"):
            pdf_buffer = generate_pdf(secure_emp_data)
            st.success("PaySlip compiled successfully!")
            
            st.download_button(
                label="📥 Download PaySlip PDF",
                data=pdf_buffer,
                file_name=f"PaySlip_{emp_code}_{selected_month.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

    # SECTION 2: CHANGE PASSWORD
    elif menu == "Change Password":
        st.subheader("🔑 Update Account Security Credentials")
        
        with st.form("password_change_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            change_btn = st.form_submit_button("Update Password")
            
            if change_btn:
                if current_password != user_info["password"]:
                    st.error("Current password incorrect.")
                elif new_password != confirm_password:
                    st.error("New passwords do not match.")
                elif len(new_password) < 6:
                    st.warning("Password should be at least 6 characters long for optimal corporate safety.")
                else:
                    st.session_state.user_db[emp_code]["password"] = new_password
