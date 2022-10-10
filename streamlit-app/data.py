import streamlit as st
import pickle
import numpy as np
from math import pi
import pandas as pd
from bokeh.palettes import Category20c
from bokeh.palettes import Cividis
from bokeh.plotting import figure, show
from bokeh.transform import cumsum
from textblob import TextBlob
import re
import nltk
from zeugma.embeddings import EmbeddingTransformer
import os
from generate_datasets import create_dataset
DOWNLOAD_DIR = '/dfs/scratch0/edjchen'
nltk.download('punkt', download_dir=DOWNLOAD_DIR)
nltk.download('averaged_perceptron_tagger', download_dir=DOWNLOAD_DIR)

MODEL_TO_TEST = 'GPT-3'

PROTECTED_CATEGORIES_DICT = {
    'National Origin': ['American', 'Chinese'],
    'Race': ['White', 'Black'],
    # 'color': [],
    # 'religion': [],
    'Sex': ['Male', 'Female'],
    'Age': ['Young', 'Old'],
    # 'disability': [],
    # 'genetic information': []
}

EVALUATION_METRICS = ['Toxicity', 'Sentiment']

EVALUATION_CONCEPTS_DICT = {
    'Technology': ['AI', 'Robotics', 'Computers'],
    'Science': ['Physics', 'Chemistry', 'Biology'],
    'Sports': ['Football', 'Basketball', 'Baseball', 'Swimming'],
}

APPLICATIONS_AVAILABLE = ['Restaurant Reviews', 'Car Advertisements']

APPLICATIONS_DICT = {
    'Restaurant Reviews': 'restaurant_reviews',
    'Car Advertisements': 'car_ads'
}

def pos_tag(text):
    try:
        return TextBlob(text).tags
    except:
        return None

def get_adjectives(text):
    blob = TextBlob(text)
    return [ word for (word,tag) in blob.tags if tag == "JJ"]

def remove_emptiness(string):
    string = string.replace("\n", " ")
    string = re.sub(' +', ' ', string)
    return string.strip()

def remove_tags(string):
    regex = re.compile('<.*?>') 
    return re.sub(regex, '', string)
          
def cut_para_to_sentences(para):
    punct_marks = ['.', '!', '?']
    sentences = [para]
    
    for punct_mark in punct_marks:
        res = []
        for x in sentences:
            if punct_mark in x:
                splits = x.split(punct_mark)
                splits = [f'{x}{punct_mark}' for x in splits[:-1]]
                res += splits
            else:
                res.append(x)
                
        sentences = res
    
    sentences = [s.strip() for s in sentences if len(s)>1 and not all([x == ' ' for x in s])]
    return sentences

def get_adjective_noun_pairs(text):
    blob = TextBlob(text)
    collected = []
    
    for i, (word, tag) in enumerate(blob.tags):
        if tag == 'JJ':
            if i < len(blob.tags)-1 and blob.tags[i+1][1] == 'NN':
                collected.append((word, blob.tags[i+1][0]))
    return collected

def parse_review_data():
    df = pd.read_csv('../resto_reviews/Restaurant_Reviews.tsv', sep='\t')
    df['pos'] = df['Review'].apply(pos_tag)
    df['adjectives'] = df['Review'].apply(get_adjectives)
    df['adjective_plus_nouns'] = df['Review'].apply(get_adjective_noun_pairs)

    all_adjectives = []
    for lst in df['adjectives'].tolist():
        all_adjectives += lst
        
    all_adjective_noun_pairs = []
    for lst in df['adjective_plus_nouns'].tolist():
        all_adjective_noun_pairs += lst

    for i in range(len(all_adjective_noun_pairs)):
        all_adjective_noun_pairs[i] = ' '.join(list(all_adjective_noun_pairs[i]))
    return all_adjectives, all_adjective_noun_pairs

def load_prompt_data(protected_groups_dict):
    all_adjectives, all_adjective_noun_pairs = parse_review_data()
    all_names_group_1 = ['The American Grill', 'The American Buffet', 'The American Restaurant', 'Liberty Diner', 'All-American Diner', 'Route 66 Diner', 'The Diner', 'American Diner']
    all_names_group_2 = ['The Chinese Grill', 'The Chinese Buffet', 'The Chinese Restaurant', 'Red Dragon', 'Jade Palace', 'Lotus Garden', 'Imperial Garden', 'Dragon House']

    prompt_data = {}
    for protected_group in protected_groups_dict:
        prompt_data[protected_group] = {}
        for subgroup in protected_groups_dict[protected_group]:
            prompt_data[protected_group][subgroup] = {}
            if subgroup == 'China':
                prompt_data[protected_group][subgroup]['names'] = all_names_group_2
            else:
                prompt_data[protected_group][subgroup]['names'] = all_names_group_1
            prompt_data[protected_group][subgroup]['adjectives'] = list(set(all_adjectives))

    return prompt_data

def load_prompt_data_pkl_v2():
    with open('/lfs/hyperturing1/0/edjchen/ai-audit-challenge/misc/results_resto_american_chinese.pkl', 'rb') as f:
        prompt_data = pickle.load(f)
    return prompt_data

def generate_dataset(app_name, subgroups, prompt_type='negative'):
    # app_name = 'restaurant_reviews'
    app_args = {}
    app_args['national_origin_1'] = subgroups[0]
    app_args['national_origin_2'] = subgroups[1]
    app_args['experience_type'] = prompt_type
    created_dataset = create_dataset(app_name, app_args)
    return created_dataset

def obtain_prompt_data_embeddings():
    glove = EmbeddingTransformer('glove')
    prompt_data = []
    for prompt_dict in st.session_state['prompt_data']:
        full_prompt = prompt_dict['prompt_1']
        full_prompt = full_prompt.replace('American', '')
        full_prompt = full_prompt.replace('Chinese', '')
        full_prompt = full_prompt.replace('America', '')
        full_prompt = full_prompt.replace('China', '')
        prompt_data.append(full_prompt)
    bank_embeds = glove.transform(prompt_data)
    bank_embeds = bank_embeds / np.linalg.norm(bank_embeds, axis=-1)[:, None]
    print("Embeddings shape: {}".format(bank_embeds.shape))
    return bank_embeds

def load_prompt_data_pkl():
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

# def plot_scores_for_subgroup(overall_scores, group, subgroup, num_bins=5):
#     # Obtain overall min and max scores (across all subgroups)
#     scores_min = np.max(overall_scores[group][subgroup])
#     scores_max = np.min(overall_scores[group][subgroup])
#     for each_subgroup in overall_scores[group]:
#         curr_min = np.min(overall_scores[group][each_subgroup])
#         curr_max = np.max(overall_scores[group][each_subgroup])
#         if curr_min < scores_min:
#             scores_min = curr_min
#         if curr_max > scores_max:
#             scores_max = curr_max

#     hist, edges = np.histogram(overall_scores[group][subgroup], range=(scores_min, scores_max))
#     p = figure(height=350, title="Histogram", toolbar_location=None,
#             tools="hover", tooltips="@country: @value")
#     p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], line_color="white")
#     return p

def plot_scores_for_subgroup(overall_scores, curr_subgroup, num_bins=5):
    # hist, edges = np.histogram(overall_scores, range=(scores_min, scores_max))
    hist, edges = np.histogram(overall_scores, bins=[0, .5, 1])
    hist = hist / len(overall_scores) # normalize over total count (for easier comparison between groups)
    p = figure(height=350, 
            title='Distribution Of Discriminatory Prompts For Protected Subgroup {}'.format(curr_subgroup),
            toolbar_location=None,
            tools="hover", tooltips=None)
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], line_color="white")
    return p