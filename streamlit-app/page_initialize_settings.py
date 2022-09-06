import streamlit as st
import data as data
from streamlit.errors import DuplicateWidgetID

# On click functions
def start_audit_on_click():
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

def evaluation_metric_on_click(metric):
    if st.session_state['metric_{}'.format(metric)] == True:
        st.session_state.evaluation_metrics.append(metric)
    else:
        st.session_state.evaluation_metrics.remove(metric)

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

# Page display function
def page_initialize_settings():
    st.title("AI Audit Settings")
    st.header("Model: {}".format(data.MODEL_TO_TEST))

    col1, col2, col3 = st.columns((1, 1, 1))
    if 'protected_groups' not in st.session_state:
        st.session_state.protected_groups = {}
    if 'evaluation_metrics' not in st.session_state:
        st.session_state.evaluation_metrics = []
    if 'evaluation_concepts' not in st.session_state:
        st.session_state.evaluation_concepts = {}

    # Display the protected groups/subgroups
    with col1:
        st.subheader("Protected Groups")
        for group, subgroups in data.PROTECTED_CATEGORIES_DICT.items():
            st.write(group)
            select_group = st.checkbox('Select All', key='group_{}'.format(group), on_change=select_all_groups_on_click, args=(group,))
            for subgroup in subgroups:
                select_subgroup = st.checkbox(subgroup, key='subgroup_{}'.format(subgroup), on_change=subgroup_on_click, args=(group, subgroup))

    # Display the evaluation metrics
    with col2:
        st.subheader("Evaluation Metrics")
        for metric in data.EVALUATION_METRICS:
            st.checkbox(metric, key='metric_{}'.format(metric), on_change=evaluation_metric_on_click, args=(metric,))

    # Display the evaluation concepts
    with col3:
        st.subheader("Evaluation Concepts")
        for concept, subconcepts in data.EVALUATION_CONCEPTS_DICT.items():
            concept_expander = st.expander(concept)
            with concept_expander:
                for subconcept in subconcepts:
                    try:
                        st.checkbox(subconcept, key='subconcept_{}'.format(subconcept), on_change=subconcept_on_click, args=(concept, subconcept))
                    except DuplicateWidgetID:
                        pass
                add_subconcept_field = st.text_input('Add a subconcept', key='add_subconcept_field_{}'.format(concept))
                add_subconcept_button = st.button('Add', key='add_subconcept_button_{}'.format(concept), on_click=add_subconcept_on_click, args=(concept_expander, concept, add_subconcept_field))

        # Create some space and add button to start audit on next page
        st.markdown('#')
        st.markdown('#')
        st.markdown('#')
        st.button('Start Audit', on_click=start_audit_on_click)

    print("Protected Groups: {}".format(st.session_state.protected_groups))
    print("Evaluation Metrics: {}".format(st.session_state.evaluation_metrics))
    print("Evaluation Concepts: {}".format(st.session_state.evaluation_concepts))