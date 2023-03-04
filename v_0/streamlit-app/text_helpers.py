''' text helpers '''
import re

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
