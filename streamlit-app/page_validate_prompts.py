import streamlit as st

# On click functions
def back_to_settings_on_click():
    st.session_state.current_page = 'initialize_settings'

def start_audit_on_click():
    st.session_state.current_page = 'perform_audit'

# Page display function
def page_validate_prompts():
    st.title('Validate Prompts')
    st.header('Please validate the following prompts to be used in the audit. Select the checkbox to deem the respective prompt invalid.')

    if 'curr_prompt_idx' not in st.session_state:
        st.session_state.curr_prompt_idx = 0

    selected_groups_list = list(st.session_state.protected_groups.keys())
    tabs_list = st.tabs(selected_groups_list)
    for tab_idx, curr_tab in enumerate(tabs_list):
        curr_group = selected_groups_list[tab_idx]
        # the number of subgroups for the current group represents the number of prompts to display
        curr_subgroups = list(st.session_state.protected_groups[curr_group].keys())
        col1, col2 = curr_tab.columns((1, 1))
        col1.subheader('Names')
        col2.subheader('Adjectives')
        for curr_subgroup_idx in range(len(curr_subgroups)):
            curr_subgroup = curr_subgroups[curr_subgroup_idx]
            curr_subgroup_names = st.session_state['prompt_data'][curr_group][curr_subgroup]['names']
            curr_subgroup_adjs = st.session_state['prompt_data'][curr_group][curr_subgroup]['adjectives'][:50]
            for curr_name in curr_subgroup_names:
                col1.checkbox(curr_name, key='{}_{}_{}'.format(curr_group, curr_subgroup, curr_name))
            for curr_adj in curr_subgroup_adjs:
                col2.checkbox(curr_adj, key='{}_{}_{}'.format(curr_group, curr_subgroup, curr_adj))

    page_col1, page_col2 = st.columns((2, 0.40))
    page_col1.button('Back To Settings', on_click=back_to_settings_on_click)
    page_col2.button('Start Audit', on_click=start_audit_on_click)