import streamlit as st
import numpy as np
import data as data

# On click functions
def back_to_settings_on_click():
    st.session_state.current_page = 'initialize_settings'

# Page display function
def page_audit_report():
    st.title('AI Audit Report')

    # scores_dict = data.calculate_subgroup_scores()

    selected_groups_list = list(st.session_state.protected_groups.keys())
    tabs_list = st.tabs(selected_groups_list)
    for tab_idx, curr_tab in enumerate(tabs_list):
        curr_group = selected_groups_list[tab_idx]

        # curr_fig = data.plot_scores_for_group(scores_dict, curr_group)
        # curr_tab.bokeh_chart(curr_fig, use_container_width=False)

        num_subgroups = len(st.session_state.protected_groups[curr_group])
        curr_subgroups = list(st.session_state.protected_groups[curr_group].keys())
        curr_tab_col_lengths = [1 for _ in range(num_subgroups)]
        curr_tab_cols = curr_tab.columns(tuple(curr_tab_col_lengths))
        for curr_tab_col_idx, curr_tab_col in enumerate(curr_tab_cols):
            curr_subgroup = curr_subgroups[curr_tab_col_idx]
            # curr_tab_score = scores_dict[curr_group][curr_subgroup]
            curr_tab_col.write('{}'.format(curr_subgroup))
            curr_fig = data.plot_scores_for_subgroup(st.session_state.user_ranks, curr_group, curr_subgroup)
            curr_tab_col.bokeh_chart(curr_fig, use_container_width=False)
            # curr_tab_col.metric(label='Score', value=curr_tab_score)
            # curr_tab_col.write('Concepts')

    st.button('Back To Settings', on_click=back_to_settings_on_click)