MODEL_TO_TEST = 'GPT-3'

PROTECTED_CATEGORIES_DICT = {
    'Race': ['White', 'Black'],
    # 'color': [],
    # 'religion': [],
    'Sex': ['Male', 'Female'],
    # 'national origin': [],
    'Age': ['Young', 'Old'],
    # 'disability': [],
    # 'genetic information': []
}

EVALUATION_METRICS = ['Toxicity', 'Fluency', 'Length']

EVALUATION_CONCEPTS_DICT = {
    'Technology': ['AI', 'Robotics', 'Computers'],
    'Science': ['Physics', 'Chemistry', 'Biology'],
    'Sports': ['Football', 'Basketball', 'Baseball'],
}