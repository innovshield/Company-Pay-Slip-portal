import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# 1. पेज कॉन्फ़िगरेशन (सबसे ऊपर होना अनिवार्य है)
st.set_page_config(page_title="Corporate PaySlip Portal", page_icon="🔒", layout="centered")

# 🔒 CSS कोड: तीन डॉट्स (MainMenu) और फुटर (Footer) को छुपाने के लिए
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 🔑 सुरक्षित एम्प्लोयी डेटाबेस (Testing के लिए इसे हुबहू इनपुट करें)
EMPLOYEE_DB = {
    "IS-10245": {
        "password": "password123",
        "Month": "October 2026",
        "Employee Name": "Aarav Sharma",
        "Department": "Engineering",
        "Designation": "Senior Cloud Architect",
        "BankAccount": "XXXXXX123456",
        "PAN_UAN": "ABCDE1234F",
        "Basic": 75000,
        "HRA": 30000,
        "Special Allowance": 15000,
        "PF Deduction": 9000,
        "Professional Tax": 200
    }
}

# 📄 DYNAMIC PDF GENERATION FUNCTION
def generate_pdf(emp_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=30, 
        leftMargin=30, 
        topMargin=30, 
        bottomMargin=30,
        title="Employee PaySlip"
    )
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
        [Paragraph(f"<b>Emp Code:</b> {emp_data.get('EmployeeCode', 'N/A')}", normal_style), Paragraph(f"<b>Name:</b> {emp_data.get('Employee Name', 'N/A')}", normal_style)],
        [Paragraph(f"<b>Department:</b> {emp_data.get('Department', 'N/A')}", normal_style), Paragraph(f"<b>Designation:</b> {emp_data.get('Designation', 'N/A')}", normal_style)],
        [Paragraph(f"<b>Bank Account:</b> {emp_data.get('BankAccount', 'N/A')}", normal_style), Paragraph(f"<b>PAN / UAN:</b> {emp_data.get('PAN_UAN', 'N/A')}", normal_style)]
    ]
    
    # फिक्स कॉलम विड्थ (540 टोटल विड्थ)
    info_table = Table(info_data, colWidths=[270, 270])
    info_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))
    
    breakdown_headers = [
        [Paragraph("Earnings Component", header_text_style), Paragraph("Amount (₹)", header_text_style),
         Paragraph("Deductions Component", header_text_style), Paragraph("Amount (₹)", header_text_style)]
    ]
    
    basic = float(emp_data.get('Basic', 0))
    hra = float(emp_data.get('HRA', 0))
    allowance = float(emp_data.get('Special Allowance', 0))
    pf = float(emp_data.get('PF Deduction', 0))
    tax = float(emp_data.get('Professional Tax', 0))
    
    total_earnings = basic + hra + allowance
    total_deductions = pf + tax
    net_pay = total_earnings - total_deductions
    
    breakdown_rows = [
        [Paragraph("Basic Salary", normal_style), Paragraph(f"{basic:,.2f}", normal_style), Paragraph("Provident Fund (PF)", normal_style), Paragraph(f"{pf:,.2f}", normal_style)],
        [Paragraph("House Rent Allowance (HRA)", normal_style), Paragraph(f"{hra:,.2f}", normal_style), Paragraph("Professional Tax", normal_style), Paragraph(f"{tax:,.2f}", normal_style)],
        [Paragraph("Special Allowance", normal_style), Paragraph(f"{allowance:,.2f}", normal_style), Paragraph("", normal_style), Paragraph("", normal_style)],
        [Paragraph("<b>Total Earnings</b>", bold_style), Paragraph(f"<b>{total_earnings:,.2f}</b>", bold_style), Paragraph("<b>Total Deductions</b>", bold_style), Paragraph(f"<b>{total_deductions:,.2f}</b>", bold_style)]
    ]
    
    # फिक्स कॉलम विड्थ ब्रेकडाउन तालिकाओं के लिए
    financial_table = Table(breakdown_headers + breakdown_rows, colWidths=[160, 110, 160, 110])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (1,1), (1,-1), 'RIGHT'),
        ('ALIGN', (3,1), (3,-1), 'RIGHT'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#EDF2F7")),
    ]))
    story.append(financial_table)
    story.append(Spacer(1, 15))
    
    net_pay_data = [[Paragraph(f"<b>NET TAKE-HOME PAY:</b> ₹ {net_pay:,.2f}", bold_style)]]
    net_pay_table = Table(net_pay_data, colWidths=[540])
    net_pay_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#C6F6D5")), 
        ('BORDER', (0,0), (-1,-1), 1, colors.HexColor("#38A169")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(net_pay_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# 🔒 SECURE LOGIN & DOWNLOAD PORTAL INTERFACE
st.title("🔒 Secure Corporate PaySlip Portal")
st.write("Please enter your credentials to download your Pay Slip.")

emp_code = st.text_input("Employee Code (e.g., IS-10245)").strip()
password = st.text_input("Password", type="password")

if st.button("Verify & Access Pay Slip"):
    if emp_code in EMPLOYEE_DB:
        if EMPLOYEE_DB[emp_code]["password"] == password:
            st.success(f"Welcome, {EMPLOYEE_DB[emp_code]['Employee Name']}! Your Pay Slip is ready.")
            
            emp_data = EMPLOYEE_DB[emp_code].copy()
            emp_data["EmployeeCode"] = emp_code
            
            # बिना एरर के PDF जनरेट होगी
            pdf_bytes = generate_pdf(emp_data)
            
            st.download_button(
                label="📥 Download PaySlip PDF",
                data=pdf_bytes,
                file_name=f"PaySlip_{emp_code}.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Incorrect Password. Please try again.")
    else:
        st.error("Employee Code not found. Please check the code and try again.")
