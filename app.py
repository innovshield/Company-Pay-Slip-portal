import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import os

st.set_page_config(page_title="Corporate PaySlip Portal", page_icon="🔒", layout="centered")

# 🔒 SECURITY BLOCK: Top Header, Menus aur Deploy buttons ko hide karne ke liye CSS
st.markdown("""
    <style>
    [data-testid="stHeader"] {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .stAppDeployButton {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("🔒 Secure Corporate PaySlip Portal")

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
    
    # Employee Master Profile Information Block (Fixed colWidths)
    info_data = [
        [Paragraph(f"<b>Emp Code:</b> {emp_data.get('EmployeeCode', '')}", normal_style)]
    ]
    # (Bacha hua code aapka as-it-is aage chalega)
