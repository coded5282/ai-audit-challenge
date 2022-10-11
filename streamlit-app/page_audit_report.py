import streamlit as st
import numpy as np
import data as data

# On click functions
def back_to_settings_on_click():
    st.session_state.current_page = 'initialize_settings'

# Helper functions
def flatten(l):
    return [item for sublist in l for item in sublist]

def curve_fitting_extrapolation(curr_group, curr_subgroup):
    if 'curve_fitting_algo' not in st.session_state:
        raise Exception('Curve fitting algo not implemented!')
    human_values_0, extrapolated_values_0 = st.session_state['curve_fitting_algo'].fit_and_predict(label_of_interest=0, subgroup_of_interest=curr_subgroup, min_cos_sim=0.92, idx2labels=st.session_state.idx2labels[curr_group][curr_subgroup])
    human_values_1, extrapolated_values_1 = st.session_state['curve_fitting_algo'].fit_and_predict(label_of_interest=1, subgroup_of_interest=curr_subgroup, min_cos_sim=0.92, idx2labels=st.session_state.idx2labels[curr_group][curr_subgroup])
    extrapolated_scores = [0 for _ in range(len(flatten(extrapolated_values_0)))]
    extrapolated_scores.extend([1 for _ in range(len(flatten(extrapolated_values_1)))])
    values_dict = {'human': [human_values_0, human_values_1],
                   'extrapolated': [extrapolated_values_0, extrapolated_values_1]
                   }
    return values_dict, extrapolated_scores

def display_col_exemplars(curr_tab_col, curr_subgroup, curr_subgroups, scores_dict):
    num_subgroups = len(curr_subgroups)
    human_scores_idxs_lists = scores_dict['human']
    extrapolated_scores_idxs_lists = scores_dict['extrapolated']
    score_tabs = curr_tab_col.tabs(['Score {}'.format(curr_score) for curr_score in range(len(human_scores_idxs_lists))])
    for human_score_idx_list_idx, human_score_idx_list in enumerate(human_scores_idxs_lists):
        if human_score_idx_list_idx == 0:
            score_tabs[human_score_idx_list_idx].markdown('Discriminatory prompts for which the protected subgroup **_{}_** has a lower value of **_{}_**'.format(curr_subgroup, st.session_state.metric))
        elif human_score_idx_list_idx == 1:
            score_tabs[human_score_idx_list_idx].markdown('Discriminatory prompts for which the protected subgroup **_{}_** has a higher value of **_{}_**'.format(curr_subgroup, st.session_state.metric))
        extrapolated_score_idx_list = extrapolated_scores_idxs_lists[human_score_idx_list_idx]
        for human_score_idx, human_score_idx_val in enumerate(human_score_idx_list):
            curr_human_score_extrapolated_idxs_list = extrapolated_score_idx_list[human_score_idx]
            curr_prompt_expander = score_tabs[human_score_idx_list_idx].expander('Prompt {}'.format(human_score_idx))
            # Display human-selected prompt-responses
            # curr_prompt_expander.header('Human')
            curr_prompt_expander.markdown('<h1 align="center">Human</h1>', unsafe_allow_html=True)
            human_subgroup_responses = []
            curr_prompt_expander.subheader('Input (Prompts):')
            for subgroup in range(num_subgroups):
                curr_human_prompt = st.session_state.prompt_data[human_score_idx_val]['prompt_{}'.format(subgroup+1)] # string
                curr_human_responses = st.session_state.prompt_data[human_score_idx_val]['responses_{}'.format(subgroup+1)] # list of strings
                human_subgroup_responses.append(curr_human_responses)
                curr_prompt_expander.markdown('**_Subgroup: {}_**'.format(curr_subgroups[subgroup]))
                curr_human_prompt_lines = curr_human_prompt.split('\n\n')
                for curr_human_prompt_line in curr_human_prompt_lines:
                    curr_prompt_expander.markdown('&nbsp;&nbsp;&nbsp;&nbsp; {}'.format(curr_human_prompt_line))
            curr_prompt_expander.subheader('Output (Responses):')
            for curr_human_response_idx in range(len(human_subgroup_responses[0])):
                for subgroup in range(num_subgroups):
                    curr_prompt_expander.markdown('**_Subgroup: {}_**'.format(curr_subgroups[subgroup]))
                    curr_prompt_expander.write('{}. {}'.format(curr_human_response_idx+1, human_subgroup_responses[subgroup][curr_human_response_idx]))
                curr_prompt_expander.write('\n')
            # Display extrapolated prompt-responses
            # curr_prompt_expander.header('Extrapolated')
            curr_prompt_expander.markdown('<h1 align="center">Extrapolated</h1>', unsafe_allow_html=True)
            if len(curr_human_score_extrapolated_idxs_list) == 0:
                curr_prompt_expander.write('No extrapolated responses for this prompt.')
            for curr_human_score_extrapolated_idx in curr_human_score_extrapolated_idxs_list:
                extrapolated_subgroup_responses = []
                curr_prompt_expander.subheader('Input (Prompts):')
                for subgroup in range(num_subgroups):
                    curr_extrapolated_prompt = st.session_state.prompt_data[curr_human_score_extrapolated_idx]['prompt_{}'.format(subgroup+1)]
                    curr_extrapolated_responses = st.session_state.prompt_data[curr_human_score_extrapolated_idx]['responses_{}'.format(subgroup+1)]
                    extrapolated_subgroup_responses.append(curr_extrapolated_responses)
                    curr_prompt_expander.markdown('**_Subgroup: {}_**'.format(curr_subgroups[subgroup]))
                    curr_extrapolated_prompt_lines = curr_extrapolated_prompt.split('\n\n')
                    for curr_extrapolated_prompt_line in curr_extrapolated_prompt_lines:
                        curr_prompt_expander.markdown('&nbsp;&nbsp;&nbsp;&nbsp; {}'.format(curr_extrapolated_prompt_line))
                curr_prompt_expander.subheader('Output (Responses):')
                for curr_extrapolated_response_idx in range(len(extrapolated_subgroup_responses[0])):
                    for subgroup in range(num_subgroups):
                        curr_prompt_expander.markdown('**_Subgroup: {}_**'.format(curr_subgroups[subgroup]))
                        curr_prompt_expander.write('{}. {}'.format(curr_extrapolated_response_idx+1, extrapolated_subgroup_responses[subgroup][curr_extrapolated_response_idx]))
                    curr_prompt_expander.write('\n')

# Page display function
def page_audit_report():
    st.title('AI Audit Report')
    # scores_dict = data.calculate_subgroup_scores()
    selected_groups_list = list(st.session_state.protected_groups.keys())
    tabs_list = st.tabs(selected_groups_list)
    for tab_idx, curr_tab in enumerate(tabs_list):
        curr_group = selected_groups_list[tab_idx]
        num_subgroups = len(st.session_state.protected_groups[curr_group])
        curr_subgroups = list(st.session_state.protected_groups[curr_group].keys())
        curr_tab_col_lengths = [1 for _ in range(num_subgroups)]
        curr_tab_cols = curr_tab.columns(tuple(curr_tab_col_lengths))
        for curr_tab_col_idx, curr_tab_col in enumerate(curr_tab_cols):
            curr_subgroup = curr_subgroups[curr_tab_col_idx]
            scores_dict, extrapolated_scores = curve_fitting_extrapolation(curr_group, curr_subgroup)

            curr_tab_col.write('{}'.format(curr_subgroup))
            curr_fig = data.plot_scores_for_subgroup(extrapolated_scores, curr_subgroup)
            curr_tab_col.bokeh_chart(curr_fig, use_container_width=False)
            curr_tab_col.write('The bar on the left displays the overall proportion of discriminatory prompts for which the protected subgroup {} has a lower value of {}.'.format(curr_subgroup, st.session_state.metric))
            curr_tab_col.write('The bar on the right displays the overall proportion of discriminatory prompts for which the protected subgroup {} has a higher value of {}.'.format(curr_subgroup, st.session_state.metric))

            display_col_exemplars(curr_tab_col, curr_subgroup, curr_subgroups, scores_dict)

            # curr_tab_col.metric(label='Score', value=curr_tab_score)
            # curr_tab_col.write('Concepts')
    st.button('Back To Settings', on_click=back_to_settings_on_click)