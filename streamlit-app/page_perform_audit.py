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
    num_prompts = 2 # just temporary variable
    for i in range(num_prompts):
        with st.container():
            col1, col2 = st.columns((2, 1))
            with col1:
                st.write("Prompt {}".format(i))
            with col2:
                curr_rank = st.selectbox('Rank', [1, 2], key='rank_{}'.format(i))

    st.button('Back To Settings', on_click=back_to_settings_on_click)
    st.button('Go To Report', on_click=go_to_report_on_click)