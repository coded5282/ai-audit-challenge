import streamlit as st
import numpy as np
import data as data
import matplotlib.pyplot as plt
import matplotlib as mpl

# On click functions
def back_to_settings_on_click():
    st.session_state.current_page = 'initialize_settings'

def start_audit_on_click():
    st.session_state.current_page = 'perform_audit'

# Helper functions
def obtain_auto_classifier_scores(response_list, auto_classifier):
    classifier_scores = []
    for response in response_list:
        c_scores = auto_classifier.predict([response])
        curr_score = c_scores.max()
        classifier_scores.append(curr_score)
    return classifier_scores

def plot_hist(arr1, arr2, group_names, bins=None, name=None, save_path=None, xlabel=None, ylabel=None):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist([arr1, arr2], bins=bins, histtype='bar', color=['red', 'blue'], label=group_names)
    ax.legend(prop={'size': 10})
    if name is not None: ax.set_title(name, wrap=True)
    if xlabel is not None: ax.set_xlabel(xlabel)
    if ylabel is not None: ax.set_ylabel(ylabel)
    # ax.xticks(bins)
    return fig

def obtain_response_scores_for_subgroup(curr_subgroup_idx):
    all_scores = []
    for full_prompt_idx in range(len(st.session_state['prompt_data'])):
        model_responses = st.session_state['prompt_data'][full_prompt_idx]['responses_{}'.format(curr_subgroup_idx+1)]
        curr_scores = obtain_auto_classifier_scores(model_responses, st.session_state['auto_classifier'])
        all_scores.extend(curr_scores)
    return all_scores

def find_subgroups_for_comparison():
    groups_list = list(st.session_state.protected_groups.keys())
    for group in groups_list:
        if len(list(st.session_state.protected_groups[group].keys())) == 2:
            return group

# Page display function
def page_auto_metric_report():
    st.title('Automated {} Classifier Metric Report'.format(st.session_state.metric))
    subgroup_0_scores = obtain_response_scores_for_subgroup(0)
    subgroup_1_scores = obtain_response_scores_for_subgroup(1)
    subgroups_for_comparison = find_subgroups_for_comparison()
    hist_fig = plot_hist(
        arr1 = subgroup_0_scores,
        arr2 = subgroup_1_scores,
        bins = np.arange(0, 1, 0.1),
        name = '{} Scores, {} Application'.format(st.session_state.metric, st.session_state.application),
        group_names = list(st.session_state.protected_groups[subgroups_for_comparison].keys()),
        xlabel = '{} Scores (Higher Is More Toxic)'.format(st.session_state.metric),
        ylabel = 'Frequency',
    )
    st.pyplot(hist_fig)
    st.button('Back To Settings', on_click=back_to_settings_on_click)
    st.button('Proceed', on_click=start_audit_on_click)