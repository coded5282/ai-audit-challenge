import os
os.environ['GENSIM_DATA_DIR'] = '/lfs/hyperturing1/0/edjchen/temp/'
import streamlit as st
from page_initialize_settings import page_initialize_settings
from page_perform_audit import page_perform_audit
from page_audit_report import page_audit_report
from page_validate_prompts import page_validate_prompts
import data as data
import automated_classifiers as automated_classifiers
import models as models
import algos as algos
from persist import persist, load_widget_state

load_widget_state()

print("Starting new page!")
st.set_page_config(layout="wide")

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'initialize_settings'
if 'prev_page' not in st.session_state:
    st.session_state.prev_page = 'initialize_settings'

# TEMPORARY: Load prompt data from pickle files
# st.session_state['prompt_data'] = data.load_prompt_data()
# st.session_state['auto_classifier'] = automated_classifiers.get_auto_classifier('Toxicity')

def find_subgroups_for_comparison():
    groups_list = list(st.session_state.protected_groups.keys())
    for group in groups_list:
        if len(list(st.session_state.protected_groups[group].keys())) == 2:
            return group

# Display the current page
if st.session_state.current_page == 'initialize_settings':
    page_initialize_settings()
    st.session_state.prev_page = 'initialize_settings'
elif st.session_state.current_page == 'validate_prompts':
    st.session_state['prompt_data'] = data.load_prompt_data(st.session_state.protected_groups)
    page_validate_prompts()
    st.session_state.prev_page = 'validate_prompts'
elif st.session_state.current_page == 'perform_audit':
    # TODO: For now, is only using the first evaluation metric
    # st.session_state['prompt_data'] = data.load_prompt_data_pkl_v2() # TEMPORARY
    if st.session_state.prev_page == 'initialize_settings':
        with st.spinner('Loading data and algorithms...'):
            subgroups_for_comparison = find_subgroups_for_comparison()
            st.session_state['prompt_data'] = data.generate_dataset(data.APPLICATIONS_DICT[st.session_state.application], list(st.session_state.protected_groups[subgroups_for_comparison].keys()))
            st.session_state['prompt_data_embeddings'] = data.obtain_prompt_data_embeddings() # TEMPORARY
            st.session_state['active_learning_algo'] = algos.EmbeddingsSampling(st.session_state['prompt_data_embeddings'])
            st.session_state['active_learning_algo'].update(0)
            st.session_state['curve_fitting_algo'] = algos.CosineSimFit(st.session_state['prompt_data_embeddings'])
            st.session_state['auto_classifier'] = automated_classifiers.get_auto_classifier(st.session_state.metric)
            st.session_state['eval_model'] = models.get_eval_model()
    page_perform_audit()
    st.session_state.prev_page = 'perform_audit'
elif st.session_state.current_page == 'audit_report':
    page_audit_report()
    st.session_state.prev_page = 'audit_report'