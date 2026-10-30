    elif st.session_state['user_role'] == 'employee':
        st.title("📄 Corporate Earnings Portal")
        target_code = st.session_state['emp_code']
        
        if 'salary_df' in st.session_state:
            df = st.session_state['salary_df']
            matched_rows = df[df['EmployeeCode'] == target_code]
            
            if not matched_rows.empty:
                # pandas series se single item extract karne ke liye .iloc[0] lagaya hai
                emp_data = matched_rows.iloc[0].to_dict() 
                st.success(f"Profile Authenticated: {emp_data.get('Employee Name', 'User')}")
                
                # Render Preview on Streamlit Viewport
                payslip_html = get_html_payslip(emp_data)
                st.components.v1.html(payslip_html, height=520, scroller=True)
                
                # TRIGGER CONVERSION ON DOWNLOAD INTENT
                pdf_bytes = convert_html_to_pdf(payslip_html)
                
                if pdf_bytes:
                    st.download_button(
                        label="📥 Download PaySlip as PDF",
                        data=pdf_bytes,
                        file_name=f"PaySlip_{target_code}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Could not construct PDF file binary. Please verify backend state.")
            else:
                st.error(f"Sign-in token authenticated, but record row details missing inside admin database.")
        else:
            st.warning("⚠️ The management team has not initialized the master roster for this cycle yet.")
