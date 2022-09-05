import streamlit as st

# On click functions
def back_to_settings_on_click():
    st.session_state.current_page = 'initialize_settings'

# Page display function
def page_audit_report():
    st.title('AI Audit Report')

    # TODO: Finish rest of report interface

    st.button('Back To Settings', on_click=back_to_settings_on_click)