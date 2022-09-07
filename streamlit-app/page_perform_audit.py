import streamlit as st

# On click functions
def back_to_settings_on_click():
    st.session_state.current_page = 'initialize_settings'

def go_to_report_on_click():
    st.session_state.current_page = 'audit_report'

def curr_tab_next_on_click(curr_group, curr_subgroups):
    st.session_state.curr_prompt_idx += 1
    # Store user ranking
    for i in range(len(curr_subgroups)):
        curr_rank = st.session_state['rank_{}_{}'.format(i, curr_group)]
        st.session_state.user_ranks[curr_group][curr_subgroups[i]].append(curr_rank)

# Page display function
def page_perform_audit():
    st.title('AI Audit')
    st.header('Please rank the following outputs based on the selected evaluation metric')

    if 'curr_prompt_idx' not in st.session_state:
        st.session_state.curr_prompt_idx = 0
    if 'user_ranks' not in st.session_state:
        st.session_state.user_ranks = {}

    selected_groups_list = list(st.session_state.protected_groups.keys())
    tabs_list = st.tabs(selected_groups_list)
    for tab_idx, curr_tab in enumerate(tabs_list):
        curr_group = selected_groups_list[tab_idx]
        if curr_group not in st.session_state.user_ranks:
            st.session_state.user_ranks[curr_group] = {}
        # the number of subgroups for the current group represents the number of prompts to display
        curr_subgroups = list(st.session_state.protected_groups[curr_group].keys())
        num_prompts = len(curr_subgroups)
        col1, col2, col3 = curr_tab.columns((2, 0.5, 0.5))
        for i in range(num_prompts):
            if curr_subgroups[i] not in st.session_state.user_ranks[curr_group]:
                st.session_state.user_ranks[curr_group][curr_subgroups[i]] = []
            # TODO: Replace with generated prompts
            with st.container():
                curr_prompt = st.session_state['prompt_data'][st.session_state.curr_prompt_idx]['top_response_group_{}'.format(i+1)]
                curr_metric = st.session_state['prompt_data'][st.session_state.curr_prompt_idx]['toxicity_group_{}'.format(i+1)]
                col1.write(curr_prompt)
                col1.write('\n')
                col1.write('\n')
                col2.metric(label='Automated Score', value=curr_metric)
                col2.write('\n')
                col2.write('\n')
                curr_rank = col3.selectbox('Rank', [1, 2], key='rank_{}_{}'.format(i, curr_group))
                col3.write('\n')
                col3.write('\n')
        
        col3.button('Next', key='next_{}'.format(curr_group), on_click=curr_tab_next_on_click, args=(curr_group, curr_subgroups))

    page_col1, page_col2 = st.columns((2, 0.40))
    page_col1.button('Back To Settings', on_click=back_to_settings_on_click)
    page_col2.button('Go To Report', on_click=go_to_report_on_click)