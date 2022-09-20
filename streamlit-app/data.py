import streamlit as st
import pickle
import numpy as np
from math import pi
import pandas as pd
from bokeh.palettes import Category20c
from bokeh.palettes import Cividis
from bokeh.plotting import figure, show
from bokeh.transform import cumsum

MODEL_TO_TEST = 'GPT-3'

PROTECTED_CATEGORIES_DICT = {
    'Race': ['White', 'Black'],
    # 'color': [],
    # 'religion': [],
    'Sex': ['Male', 'Female'],
    'National Origin': ['USA', 'China'],
    'Age': ['Young', 'Old'],
    # 'disability': [],
    # 'genetic information': []
}

EVALUATION_METRICS = ['Toxicity', 'Fluency', 'Length']

EVALUATION_CONCEPTS_DICT = {
    'Technology': ['AI', 'Robotics', 'Computers'],
    'Science': ['Physics', 'Chemistry', 'Biology'],
    'Sports': ['Football', 'Basketball', 'Baseball', 'Swimming'],
}

def load_prompt_data():
    # with open(f'../results_final_basketball_.pkl', 'rb') as f:
    #     data = pickle.load(f)

    with open(f'../results_final_swimming_.pkl', 'rb') as f:
        data = pickle.load(f)

    prompts_core = []
    prompts_grp_1 = []
    prompts_grp_2 = []
    responses_grp_1 = [] 
    responses_grp_2 = []
    toxicities_grp_1 = []
    toxicities_grp_2 = []
    disparities = []

    for dct in data:
        prompts_grp_1.append(dct['prompt_text_group_1'])
        prompts_grp_2.append(dct['prompt_text_group_2'])
        prompts_core.append(dct['prompt_text_group_1'].lower().replace('china', '[ COUNTRY ]'))
        responses_grp_1.append(dct['top_response_group_1'])
        responses_grp_2.append(dct['top_response_group_2'])
        toxicities_grp_1.append(dct['toxicity_group_1'])
        toxicities_grp_2.append(dct['toxicity_group_2'])
        disparities.append(abs(toxicities_grp_1[-1]-toxicities_grp_2[-1]))
    
    assert len(prompts_grp_1) == len(prompts_grp_2) == len(prompts_core) == len(responses_grp_1) == len(responses_grp_2) == len(toxicities_grp_1) == len(toxicities_grp_2) == len(disparities)

    # sort by disparity scores
    objects = list(zip(
        prompts_core, 
        prompts_grp_1, 
        prompts_grp_2, 
        responses_grp_1, 
        responses_grp_2, 
        toxicities_grp_1, 
        toxicities_grp_2, 
        disparities
    ))

    objects = sorted(objects, key = lambda x: x[-1], reverse=True)

    sorted_data = []
    for each_object in objects:
        each_dict = {}
        each_dict['prompts_core'] = each_object[0]
        each_dict['prompts_grp_1'] = each_object[1]
        each_dict['prompts_grp_2'] = each_object[2]
        each_dict['top_response_group_1'] = each_object[3]
        each_dict['top_response_group_2'] = each_object[4]
        each_dict['toxicity_group_1'] = each_object[5]
        each_dict['toxicity_group_2'] = each_object[6]
        each_dict['disparity'] = each_object[7]
        sorted_data.append(each_dict)

    return sorted_data

def calculate_subgroup_scores():
    if ('user_ranks' not in st.session_state) or ('protected_groups' not in st.session_state):
        raise Exception('User data not found in session state!')

    scores_dict = {}

    selected_groups_list = list(st.session_state.protected_groups.keys())
    for group_idx, curr_group in enumerate(selected_groups_list):
        scores_dict[curr_group] = {}
        num_subgroups = len(st.session_state.protected_groups[curr_group])
        curr_subgroups = list(st.session_state.protected_groups[curr_group].keys())
        for subgroup_idx, curr_subgroup in enumerate(curr_subgroups):
            curr_subgroup_score = np.mean(st.session_state.user_ranks[curr_group][curr_subgroup])
            scores_dict[curr_group][curr_subgroup] = curr_subgroup_score

    return scores_dict

def plot_scores_for_group(scores_dict, curr_group):
    x = scores_dict[curr_group]

    data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'country'})
    data['angle'] = data['value']/data['value'].sum() * 2*pi
    # TODO: Modify this to allow for more colors and remove constant 12    
    data['color'] = tuple(list(Category20c[12])[:len(x)])

    p = figure(height=350, title="Pie Chart", toolbar_location=None,
            tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='country', source=data)

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None
    return p