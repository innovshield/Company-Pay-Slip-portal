import os
import sys
os.system(f"{sys.executable} -m pip install reportlab openpyxl pandas streamlit")
# ----------------------------------------------------
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

st.set_page_config(page_title="Corporate PaySlip Portal", page_icon="🔒", layout="centered")
st.title("🔒 Secure Corporate PaySlip Portal")

# 📄 DYNAMIC PDF GENERATION FUNCTION
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
    
    # Company Header
    story.append(Paragraph("<b>INNOVSHIELD MANAGEMENT PVT. LTD.</b>", title_style))
    story.append(Paragraph("Qutub Vihar, Dwarka, New Delhi", subtitle_style))
    story.append(Paragraph(f"<b>Pay Slip for the Month of:</b> {emp_data.get('Month', 'N/A')}", ParagraphStyle('H3', parent=styles['Heading3'], alignment=1, spaceAfter=10)))
    story.append(Spacer(1, 5))
    
    # Employee Master Information Table
    info_data = [
        [Paragraph(f"<b>Emp Code:</b> {emp_data.get('EmployeeCode', '')}", normal_style), Paragraph(f"<b>Name:</b> {emp_data.get('Employee Name', '')}", normal_style), Paragraph(f"<b>Designation:</b> {emp_data.get('Designation', '')}", normal_style)],
        [Paragraph(f"<b>Location:</b> {emp_data.get('Location', '')}", normal_style), Paragraph(f"<b>A/c No:</b> {emp_data.get('Ac No', '')}", normal_style), Paragraph(f"<b>UAN No:</b> {emp_data.get('UAN NO', '')}", normal_style)],
        [Paragraph(f"<b>ESIC No:</b> {emp_data.get('ESIC NO', '')}", normal_style), Paragraph(f"<b>Month Days:</b> {emp_data.get('Month Days', '')}", normal_style), Paragraph(f"<b>Worked Days:</b> {emp_data.get('Worked Days', '')}", normal_style)]
    ]
    info_table = Table(info_data, colWidths=[150, 200, 190])
    info_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))
    
    # Master structure list (Component Name, Fixed Key, Earned Key, Deduction Name, Deduction Amt Key)
    # Ship/COD Loss aur EWF ko yahaan target kiya gaya hai
    all_components = [
        ("Basic Salary", "Fixed Basic", "Earn Basic", "Provident Fund (PF)", "PF"),
        ("HRA", "Fixed HRA", "Earn HRA", "ESIC", "ESIC"),
        ("Statutory Bonus", "Fixed Stat Bonus", "Earn Stat Bon", "LWF", "LWF"),
        ("Special Allowance", "Fixed Special", "Earn Special", "EWF Deduc", "EWF"),
        ("Leave Encashment", None, "Leave Encash", "Ship/COD Loss", "Ship/COD Loss"),
        ("Attendance Bonus", None, "Atte Bonus", "Salary Advance", "Advance"),
        ("Mobile Allowance", None, "Mobile Allo", "Notice Pay Deduct", "Notice Pay"),
        ("Special Incentive", None, "Special Incentive", None, None),
        ("Group Incentive", None, "Group Incentive", None, None),
        ("Arrears / Other", None, "Arrears", None, None),
        ("Incentive / Performance", None, "Incentive", None, None)
    ]
    
    # Base layout header row
    salary_table_data = [
        [Paragraph("Salary Component", header_text_style), Paragraph("Fixed Rate (₹)", header_text_style), 
         Paragraph("Earned Amount (₹)", header_text_style), Paragraph("Deductions", header_text_style), Paragraph("Amount (₹)", header_text_style)]
    ]
    
    # DYNAMIC FILTER LOGIC (Bina figure waale rows hide ho jayenge)
    for comp, f_key, e_key, ded, d_key in all_components:
        f_val = float(emp_data.get(f_key, 0)) if f_key else 0.0
        e_val = float(emp_data.get(e_key, 0)) if e_key else 0.0
        d_val = float(emp_data.get(d_key, 0)) if d_key else 0.0
        
        if f_val == 0.0 and e_val == 0.0 and d_val == 0.0 and not ded:
            continue
            
        f_text = str(int(f_val)) if f_key and f_val > 0 else "-"
        e_text = str(int(e_val)) if e_val > 0 else "-"
        d_text = str(int(d_val)) if d_key and d_val > 0 else "-"
        ded_text = ded if ded and (d_val > 0 or comp in ["Basic Salary", "HRA"]) else ""
        
        comp_text = comp if (f_val > 0 or e_val > 0 or comp in ["Basic Salary", "HRA"]) else ""
        if comp_text == "" and ded_text == "":
            continue
            
        salary_table_data.append([
            Paragraph(comp_text, normal_style), Paragraph(f_text, normal_style), Paragraph(e_text, normal_style),
            Paragraph(ded_text, normal_style), Paragraph(d_text if ded_text else "", normal_style)
        ])
        
    # Totals Row
    salary_table_data.append([
        Paragraph("<b>Gross Total</b>", bold_style), Paragraph(f"<b>{int(float(emp_data.get('Fixed Gross', 0)))}</b>", bold_style), 
        Paragraph(f"<b>{int(float(emp_data.get('Total Earn', 0)))}</b>", bold_style), Paragraph("<b>Total Deduction</b>", bold_style), Paragraph(f"<b>{int(float(emp_data.get('Total Dedu', 0)))}</b>", bold_style)
    ])
    
    # Net Pay Row
    salary_table_data.append([
        Paragraph(f"<b>NET PAYABLE TAKE-HOME SALARY: ₹{int(float(emp_data.get('Net Pay', 0)))}</b>", ParagraphStyle('NetStyle', parent=bold_style, fontSize=9, textColor=colors.HexColor("#2B6CB0"))), 
        "", "", "", ""
    ])
    
    sal_table = Table(salary_table_data, colWidths=[140, 80, 100, 130, 90])
    sal_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")), 
        ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor("#CBD5E0")),
        ('SPAN', (0,-1), (-1,-1)), 
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#EBF8FF")), 
        ('PADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (1,1), (2,-2), 'CENTER'),
        ('ALIGN', (4,1), (4,-2), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(sal_table)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("<i>Note: This is a system-generated secure slip and does not require a physical stamp or signature.</i>", normal_style))
    doc.build(story)
    buffer.seek(0)
    return buffer

# 3. DIRECT APP RUN LOGIC WITH AUTOMATIC ZERO FILL
excel_file = "salary_data.xlsx"

df = pd.read_excel(excel_file)
df.fillna(0, inplace=True)

for col in ['EmployeeCode', 'Password', 'Employee Name', 'Month']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

tab1, tab2 = st.tabs(["🔑 Employee Login Portal", "🔄 Change Password"])

# TAB 1: LOGIN & DOWNLOAD
with tab1:
    st.subheader("Apna Account Login Karein")
    with st.form("login_form"):
        emp_code_input = st.text_input("Employee Code:").strip()
        password_input = st.text_input("Password:", type="password").strip()
        submit_button = st.form_submit_button(label="Login & Download Payslip")

    if submit_button:
        if emp_code_input and password_input:
            result = df[(df['EmployeeCode'] == emp_code_input) & (df['Password'] == password_input)]
            
            if not result.empty:
                emp_data = result.iloc[0].to_dict()
                st.success(f"Welcome {emp_data.get('Employee Name')}!")
                
                pdf_data = generate_pdf(emp_data)
                st.download_button(
                    label="📥 Download Salary Slip (PDF Format)",
                    data=pdf_data,
                    file_name=f"PaySlip_{emp_code_input}_{emp_data.get('Month','Payslip')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Galat Employee Code ya Password.")
        else:
            st.warning("Kripya dono fields ko bharein.")

# TAB 2: CHANGE PASSWORD
with tab2:
    st.subheader("Naya Password Set Karein")
    with st.form("change_password_form"):
        ch_emp_code = st.text_input("Employee Code:").strip()
        ch_old_pass = st.text_input("Old / Default Password:", type="password").strip()
        ch_new_pass = st.text_input("Naya Password:", type="password").strip()
        change_button = st.form_submit_button(label="Update New Password")

    if change_button:
        if ch_emp_code and ch_old_pass and ch_new_pass:
            user_match = df[(df['EmployeeCode'] == ch_emp_code) & (df['Password'] == ch_old_pass)]
            if not user_match.empty:
                df.loc[df['EmployeeCode'] == ch_emp_code, 'Password'] = ch_new_pass
                df.to_excel(excel_file, index=False)
                st.success("Password successfully update ho chuka hai!")
            else:
                st.error("Purani details galat hain.")
        else:
            st.warning("Kripya saari fields ko sahi se bharein.")
