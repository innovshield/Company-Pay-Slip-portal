import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
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
    
    # Employee Master Profile Information Block
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
    
    # Master Matrix Breakdown Configuration
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
    
    salary_table_data = [
        [Paragraph("Salary Component", header_text_style), Paragraph("Fixed Rate (₹)", header_text_style), 
         Paragraph("Earned Amount (₹)", header_text_style), Paragraph("Deductions", header_text_style), Paragraph("Amount (₹)", header_text_style)]
    ]
    
    # Dynamic Filtering Logic to exclude zeros safely
    for comp, f_key, e_key, ded, d_key in all_components:
        f_val = float(emp_data.get(f_key, 0)) if f_key and emp_data.get(f_key) else 0.0
        e_val = float(emp_data.get(e_key, 0)) if e_key and emp_data.get(e_key) else 0.0
        d_val = float(emp_data.get(d_key, 0)) if d_key and emp_data.get(d_key) else 0.0
        
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
        
    # Aggregate Summary Row
    salary_table_data.append([
        Paragraph("<b>Gross Total</b>", bold_style), Paragraph(f"<b>{int(float(emp_data.get('Fixed Gross', 0)))}</b>", bold_style), 
        Paragraph(f"<b>{int(float(emp_data.get('Total Earn', 0)))}</b>", bold_style), Paragraph("<b>Total Deduction</b>", bold_style), Paragraph(f"<b>{int(float(emp_data.get('Total Dedu', 0)))}</b>", bold_style)
    ])
    
    # Final Payout Matrix Row
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

# --- SECURE DATA GATEKEEPER & WORKSPACE ROUTING ---
if not os.path.exists(excel_file):
    st.error(f"❌ Master Database File '{excel_file}' missing from server root directory.")
else:
    df = pd.read_excel(excel_file)
    df.fillna(0, inplace=True)
    
    for col in ['EmployeeCode', 'Password', 'Employee Name', 'Month']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # GATEKEEPER MODE: Render ONLY the login screen if not authenticated
    if not st.session_state['is_authenticated']:
        st.title("🔒 Secure Corporate PaySlip Portal")
        st.subheader("Login required to access the application")
        
        with st.form("portal_gateway_login"):
            input_user = st.text_input("Employee Code:").strip()
            input_pass = st.text_input("Password:", type="password").strip()
            login_btn = st.form_submit_button("Access Portal")
            
            if login_btn:
                if input_user and input_pass:
                    match = df[(df['EmployeeCode'] == input_user) & (df['Password'] == input_pass)]
                    if not match.empty:
                        st.session_state['is_authenticated'] = True
                        st.session_state['logged_in_user'] = input_user
                        st.success("Authorized! Loading profile dashboard...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Employee Code or Password.")
                else:
                    st.warning("Please fill in both fields.")
    else:
        # SECURE VIEWPORT FOR AUTHENTICATED USERS
        st.title("🔒 Secure Corporate PaySlip Portal")
        
        # Sidebar clean sign-out system
        st.sidebar.title("🔐 Secure Session")
        st.sidebar.write(f"Account: **{st.session_state['logged_in_user']}**")
        if st.sidebar.button("Logout Session 🚪"):
            st.session_state['is_authenticated'] = False
            st.session_state['logged_in_user'] = None
            st.rerun()
            
        tab1, tab2 = st.tabs(["🔑 Employee Login Portal", "🔄 Change Password"])
        current_emp = st.session_state['logged_in_user']
        
        # TAB 1: WORKSPACE & PDF DOWNLOAD
        with tab1:
            # Query the user row as a DataFrame
            user_df = df[df['EmployeeCode'] == current_emp]
            
