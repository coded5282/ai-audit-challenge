'''
This script generates a dataset pertaining to the application being tested
Args are provided to specify the exact dataset version (e.g. for app resto reviews: culture_1, culture_2 etc)
'''

# prompt scripts by app
from prompt_creators.restaurant_prompts import generate_restaurant_prompts

# LLM
from LLMs import GPT3, respond

def create_dataset(app_name, app_args):
    prompts = generate_prompts(app_name, app_args)
    prompts_and_responses = get_responses(prompts)
    print(prompts_and_responses)
    return prompts_and_responses
    
def generate_prompts(app_name, app_args, n_prompts=1000):
    ''' generate prompts depending on application'''

    if app_name == "restaurant_reviews":

        prompts = generate_restaurant_prompts(
            culture_1 = app_args['culture_1'],
            culture_2 = app_args['culture_2'],
            experience_type = app_args['experience_type'],
            N = n_prompts
        )[:10]

    elif app_name == "adverts":
        raise NotImplementedError

    else:
        raise NotImplementedError

    print(f'generated {len(prompts)} prompts')
    return prompts

def get_responses(prompts):
    ''' solicit responses from LLM '''
    
    #### baked in manually
    nout_per_prompt = 5
    max_tokens_per_prompt = 50
    bs = 2
    ####
    
    generator = GPT3(nout_per_prompt=nout_per_prompt, max_tokens_per_prompt=max_tokens_per_prompt)

    prompts_group_1 = [x[0] for x in prompts]
    prompts_group_2 = [x[1] for x in prompts]
    assert len(prompts_group_1) == len(prompts_group_2)

    responses_1, responses_2 = respond(prompts_group_1, prompts_group_2, generator)
    assert len(prompts_group_1) == len(prompts_group_2) == len(responses_1) == len(responses_2)

    lst = []

    for i, p in enumerate(prompts_group_1):
        dct_this = {}
        dct_this['prompt_1'] = prompts_group_1[i]
        dct_this['prompt_2'] = prompts_group_2[i]
        dct_this['responses_1'] = responses_1[i]
        dct_this['responses_2'] = responses_2[i]

        lst.append(dct_this)
    
    return lst
    
#### example for debugging ####
# app_name = "restaurant_reviews"

# app_args = {
#     'culture_1' : "Mexican",
#     'culture_2' : "Chinese",
#     'experience_type' : "negative"
# }

# data = create_dataset(app_name, app_args)

# print(data[:10])