import streamlit as st
from page_initialize_settings import page_initialize_settings
from page_perform_audit import page_perform_audit
from page_audit_report import page_audit_report
import data as data

print("Starting new page!")
st.set_page_config(layout="wide")

# Initialize session state
if "current_page" not in st.session_state:
    st.session_state.current_page = 'initialize_settings'

# TEMPORARY: Load prompt data from pickle files
st.session_state['prompt_data'] = data.load_prompt_data()

# Display the current page
if st.session_state.current_page == 'initialize_settings':
    page_initialize_settings()
elif st.session_state.current_page == 'perform_audit':
    page_perform_audit()
elif st.session_state.current_page == 'audit_report':
    page_audit_report()