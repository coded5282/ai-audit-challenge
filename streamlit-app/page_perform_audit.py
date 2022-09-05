import streamlit as st

# On click functions
def back_to_settings_on_click():
    st.session_state.current_page = 'initialize_settings'

def go_to_report_on_click():
    st.session_state.current_page = 'audit_report'

# Page display function
def page_perform_audit():
    st.title('AI Audit')
    st.header('Please rank the following outputs based on the selected evaluation metric')

    # TODO: Finish rest of ranking interface

    st.button('Back To Settings', on_click=back_to_settings_on_click)
    st.button('Go To Report', on_click=go_to_report_on_click)