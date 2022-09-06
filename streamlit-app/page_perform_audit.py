import streamlit as st

# On click functions
def back_to_settings_on_click():
    st.session_state.current_page = 'initialize_settings'

def go_to_report_on_click():
    st.session_state.current_page = 'audit_report'

def curr_tab_next_on_click(curr_group):
    pass

# Page display function
def page_perform_audit():
    st.title('AI Audit')
    st.header('Please rank the following outputs based on the selected evaluation metric')

    selected_groups_list = list(st.session_state.protected_groups.keys())
    tabs_list = st.tabs(selected_groups_list)
    for tab_idx, curr_tab in enumerate(tabs_list):
        curr_group = selected_groups_list[tab_idx]
        # the number of subgroups for the current group represents the number of prompts to display
        num_prompts = len(st.session_state.protected_groups[curr_group])
        for i in range(num_prompts):
            col1, col2, col3 = curr_tab.columns((2, 0.5, 0.5))
            # TODO: Replace with generated prompts
            col1.write("Prompt {}".format(i))
            col2.metric(label='Automated Score', value=0.0)
            curr_rank = col3.selectbox('Rank', [1, 2], key='rank_{}_{}'.format(i, curr_group))
        
        curr_tab.button('Next', on_click=curr_tab_next_on_click, args=(curr_group,))

    st.button('Back To Settings', on_click=back_to_settings_on_click)
    st.button('Go To Report', on_click=go_to_report_on_click)