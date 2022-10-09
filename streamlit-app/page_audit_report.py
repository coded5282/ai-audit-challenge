import streamlit as st
import numpy as np
import data as data

# On click functions
def back_to_settings_on_click():
    st.session_state.current_page = 'initialize_settings'

# Helper functions
def curve_fitting_extrapolation(curr_group, curr_subgroup):
    if 'curve_fitting_algo' not in st.session_state:
        raise Exception('Curve fitting algo not implemented!')
    extrapolated_values_0 = st.session_state['curve_fitting_algo'].fit_and_predict(label_of_interest=0, subgroup_of_interest=curr_subgroup, min_cos_sim=0.975, idx2labels=st.session_state.idx2labels[curr_group][curr_subgroup])
    extrapolated_values_1 = st.session_state['curve_fitting_algo'].fit_and_predict(label_of_interest=1, subgroup_of_interest=curr_subgroup, min_cos_sim=0.975, idx2labels=st.session_state.idx2labels[curr_group][curr_subgroup])
    # TODO: Leverage extrapolated values for displaying exemplars
    extrapolated_scores = [0 for _ in range(len(extrapolated_values_0))]
    extrapolated_scores.extend([1 for _ in range(len(extrapolated_values_1))])
    return extrapolated_scores

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
            extrapolated_scores = curve_fitting_extrapolation(curr_group, curr_subgroup)
            # curr_tab_score = scores_dict[curr_group][curr_subgroup]
            curr_tab_col.write('{}'.format(curr_subgroup))
            # curr_fig = data.plot_scores_for_subgroup(st.session_state.user_ranks, curr_group, curr_subgroup)
            curr_fig = data.plot_scores_for_subgroup(extrapolated_scores)
            curr_tab_col.bokeh_chart(curr_fig, use_container_width=False)
            # curr_tab_col.metric(label='Score', value=curr_tab_score)
            # curr_tab_col.write('Concepts')

    st.button('Back To Settings', on_click=back_to_settings_on_click)