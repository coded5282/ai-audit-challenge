import streamlit as st
import data as data

print("Starting new page")

st.set_page_config(layout="wide")

st.title("Protected Categories")

print(data.PROTECTED_CATEGORIES_DICT)

col1, col2, col3 = st.columns((2, 1, 1))

# Display the protected groups/subgroups
with col1:
    for group, subgroups in data.PROTECTED_CATEGORIES_DICT.items():
        st.write(group)
        for subgroup in subgroups:
            st.checkbox(subgroup)