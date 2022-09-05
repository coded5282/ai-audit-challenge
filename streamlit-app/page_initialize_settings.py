import streamlit as st
import data as data

def page_initialize_settings():
    st.title("AI Audit")
    st.header("Model: {}".format(data.MODEL_TO_TEST))

    col1, col2, col3 = st.columns((1, 1, 1))

    # Display the protected groups/subgroups
    with col1:
        st.subheader("Protected Groups")
        for group, subgroups in data.PROTECTED_CATEGORIES_DICT.items():
            st.write(group)
            for subgroup in subgroups:
                st.checkbox(subgroup)

    # Display the evaluation metrics
    with col2:
        st.subheader("Evaluation Metrics")
        for metric in data.EVALUATION_METRICS:
            st.checkbox(metric)

    # Display the evaluation concepts
    with col3:
        st.subheader("Evaluation Concepts")
        for concept, subconcepts in data.EVALUATION_CONCEPTS_DICT.items():
            with st.expander(concept):
                for subconcept in subconcepts:
                    st.checkbox(subconcept)
                add_subconcept_field = st.text_input('Add a subconcept', key='add_subconcept_field_{}'.format(concept))
                add_subconcept_button = st.button('Add', key='add_subconcept_button_{}'.format(concept))

        # Create some space and add button to start audit on next page
        st.markdown('#')
        st.markdown('#')
        st.markdown('#')
        st.button('Start Audit')