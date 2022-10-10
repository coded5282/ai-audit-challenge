import streamlit as st
import data as data
from streamlit.errors import DuplicateWidgetID

# On click functions
def start_audit_on_click():
    # st.session_state.current_page = 'validate_prompts'
    st.session_state.current_page = 'perform_audit'

def select_all_groups_on_click(group):
    if st.session_state['group_{}'.format(group)] == True:
        st.session_state.protected_groups[group] = {}
        subgroups = data.PROTECTED_CATEGORIES_DICT[group]
        for subgroup in subgroups:
            st.session_state['subgroup_{}'.format(subgroup)] = True
            st.session_state.protected_groups[group][subgroup] = {}

def subgroup_on_click(group, subgroup):
    print("IN SUBGROUP ON CLICK!")
    # unchecking checkbox
    if st.session_state['subgroup_{}'.format(subgroup)] == False:
        if group in st.session_state.protected_groups:
            if subgroup in st.session_state.protected_groups[group]:
                st.session_state.protected_groups[group].pop(subgroup, '{} not found'.format(subgroup))
            if len(st.session_state.protected_groups[group]) == 0:
                st.session_state.protected_groups.pop(group, '{} not found'.format(group))
    # checking checkbox
    else:
        if group not in st.session_state.protected_groups:
            st.session_state.protected_groups[group] = {}
        st.session_state.protected_groups[group][subgroup] = {}
    check_subgroups_overselected()

def evaluation_metric_on_click(metric):
    if st.session_state['metric_{}'.format(metric)] == True:
        st.session_state.evaluation_metrics.append(metric)
    else:
        st.session_state.evaluation_metrics.remove(metric)
    if len(st.session_state.evaluation_metrics) == 1:
        st.session_state.contains_proper_metrics = True
        st.session_state.contains_metric_errors = False
    if len(st.session_state.evaluation_metrics) >= 2:
        st.warning('You can currently only select one evaluation metric at a time. Please unselect the other metric before selecting this one.')
        st.session_state.contains_metric_errors = True
        st.session_state.contains_proper_metrics = False
    else:
        st.session_state.contains_metric_errors = False

def subconcept_on_click(concept, subconcept):
    # unchecking checkbox
    if st.session_state['subconcept_{}'.format(subconcept)] == False:
        if concept in st.session_state.evaluation_concepts:
            if subconcept in st.session_state.evaluation_concepts[concept]:
                st.session_state.evaluation_concepts[concept].pop(subconcept, '{} not found'.format(subconcept))
            if len(st.session_state.evaluation_concepts[concept]) == 0:
                st.session_state.evaluation_concepts.pop(concept, '{} not found'.format(concept))
    # checking checkbox
    else:
        if concept not in st.session_state.evaluation_concepts:
            st.session_state.evaluation_concepts[concept] = {}
        st.session_state.evaluation_concepts[concept][subconcept] = {}

def add_subconcept_on_click(concept_expander, concept, add_subconcept_field):
    data.EVALUATION_CONCEPTS_DICT[concept].append(add_subconcept_field)

def add_subgroup_on_click(group_expander, group, add_subgroup_field):
    data.PROTECTED_CATEGORIES_DICT[group].append(add_subgroup_field)

def check_subgroups_overselected():
    total_selected = 0
    multiple_groups_selected = False
    groups_list = list(st.session_state.protected_groups.keys())
    for group in groups_list:
        num_selected = len(list(st.session_state.protected_groups[group].keys()))
        if (num_selected > 0) and (total_selected > 0):
            multiple_groups_selected = True
        total_selected += num_selected
    if total_selected > 2:
        st.warning('You can currently only select two protected subgroups at a time. Please unselect the other protected categories before selecting this one.')
        st.session_state.contains_subgroup_errors = True
        st.session_state.contains_proper_subgroups = False
    if multiple_groups_selected:
        st.warning('You can currently only select two protected subgroups from the same group (i.e. Race, Age) at a time. Please unselect the other protected categories before selecting this one.')
        st.session_state.contains_subgroup_errors = True
        st.session_state.contains_proper_subgroups = False
    if (total_selected <= 2) and (not multiple_groups_selected):
        st.session_state.contains_subgroup_errors = False
        if total_selected == 2:
            st.session_state.contains_proper_subgroups = True
        else:
            st.session_state.contains_proper_subgroups = False

# Page display function
def page_initialize_settings():
    st.title("AI Audit Settings")
    st.header("Model Being Audited: {}".format(data.MODEL_TO_TEST))
    st.subheader('Please select two protected subgroups and one evaluation metric.')

    col1, col2, col3 = st.columns((1, 1, 1))
    if 'protected_groups' not in st.session_state:
        st.session_state.protected_groups = {}
    if 'evaluation_metrics' not in st.session_state:
        st.session_state.evaluation_metrics = []
    if 'evaluation_concepts' not in st.session_state:
        st.session_state.evaluation_concepts = {}
    if 'contains_subgroup_errors' not in st.session_state:
        st.session_state.contains_subgroup_errors = False
    if 'contains_metric_errors' not in st.session_state:
        st.session_state.contains_metric_errors = False
    if 'contains_proper_subgroups' not in st.session_state:
        st.session_state.contains_proper_subgroups = False
    if 'contains_proper_metrics' not in st.session_state:
        st.session_state.contains_proper_metrics = False

    # Display the protected groups/subgroups
    with col1:
        st.subheader("Protected Groups")
        for group, subgroups in data.PROTECTED_CATEGORIES_DICT.items():
            st.write(group)
            group_expander = st.expander(group)
            with group_expander:
                for subgroup in subgroups:
                    select_subgroup = st.checkbox(subgroup, key='subgroup_{}'.format(subgroup), on_change=subgroup_on_click, args=(group, subgroup))
                add_subgroup_field = st.text_input('Add a subgroup', key='add_subgroup_field_{}'.format(group))
                add_subgroup_button = st.button('Add', key='add_subgroup_button_{}'.format(group), on_click=add_subgroup_on_click, args=(group_expander, group, add_subgroup_field))
            # select_group = st.checkbox('Select All', key='group_{}'.format(group), on_change=select_all_groups_on_click, args=(group,))

    # Display the evaluation metrics
    with col2:
        st.subheader("Evaluation Metrics")
        for metric in data.EVALUATION_METRICS:
            st.checkbox(metric, key='metric_{}'.format(metric), on_change=evaluation_metric_on_click, args=(metric,))

    # Display the evaluation concepts
    with col3:
        st.subheader("Application")
        st.radio('Select an application', data.APPLICATIONS_AVAILABLE, key='application')
        # st.subheader("Evaluation Concepts")
        # for concept, subconcepts in data.EVALUATION_CONCEPTS_DICT.items():
        #     concept_expander = st.expander(concept)
        #     with concept_expander:
        #         for subconcept in subconcepts:
        #             try:
        #                 st.checkbox(subconcept, key='subconcept_{}'.format(subconcept), on_change=subconcept_on_click, args=(concept, subconcept))
        #             except DuplicateWidgetID:
        #                 pass
        #         add_subconcept_field = st.text_input('Add a subconcept', key='add_subconcept_field_{}'.format(concept))
        #         add_subconcept_button = st.button('Add', key='add_subconcept_button_{}'.format(concept), on_click=add_subconcept_on_click, args=(concept_expander, concept, add_subconcept_field))

        # Create some space and add button to start audit on next page
        st.markdown('#')
        st.markdown('#')
        st.markdown('#')
        print(st.session_state.contains_proper_subgroups)
        print(st.session_state.contains_proper_metrics)
        st.button('Validate Prompts', on_click=start_audit_on_click, disabled=(st.session_state.contains_subgroup_errors or st.session_state.contains_metric_errors) or (not st.session_state.contains_proper_metrics or not st.session_state.contains_proper_subgroups))

    print("Protected Groups: {}".format(st.session_state.protected_groups))
    print("Evaluation Metrics: {}".format(st.session_state.evaluation_metrics))
    print("Evaluation Concepts: {}".format(st.session_state.evaluation_concepts))
    print("APPLICATION: {}".format(st.session_state.application))