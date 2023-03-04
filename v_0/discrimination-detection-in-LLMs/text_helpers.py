import re
from itertools import product

'''basic utils, no changes to text'''

def to_list(string):
    return string.split(' ')

def to_string(lst):
    return ' '.join(lst)

def num_words(string):
    return len(string.split(' '))

def num_alphanums(string):
    return len(re.findall('[^a-zA-Z ]', string))

def has_no_non_alphabets(string):
    return len(re.findall('[^a-zA-Z ]', string)) == 0

def num_words(string):
    return len(to_list(string))


'''level 1: basic utils, edits allowed'''

def remove_emptiness(string):
    string = string.replace("\n", " ")
    string = re.sub(' +', ' ', string)
    return string.strip()

def remove_tags(string):
    regex = re.compile('<.*?>') 
    return re.sub(regex, '', string)
          

'''level 2: front-facing utils wrapping the above'''

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

def text_product(pre_texts, core_phrases, post_texts):
    assert type(pre_texts) == type(core_phrases) == type(post_texts)
    combinations = list(product(pre_texts, core_phrases, post_texts))
    return [' '.join(list(x)).strip() for x in combinations]

def replace_many(sentence, word_in_sentence, lst_alternatives):
    sentence = to_list(sentence)
    sentence = [x.lower() for x in sentence]
    idx_word = sentence.index(word_in_sentence.lower())
    
    res = []
    for alt in lst_alternatives:
        new = list(sentence)
        new[idx_word] = alt
        res.append(to_string(new))
    
    return res
