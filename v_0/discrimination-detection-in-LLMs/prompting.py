from text_helpers import *
from filler import Word_Filler_Hugging_Face
import numpy as np

class Phrase():
    def __init__(self, text, core_concepts, text_plausibility=None):
        text = text.lower()
        core_concepts = [x.lower() for x in core_concepts]
        for x in core_concepts:
            assert x in text, f"concept provided is not in starting text, concept={x}, text={text}"
            assert has_no_non_alphabets(x)        
        
        # store as lists
        self.text = to_list(text)
        self.core_concepts = core_concepts
        
        self.concept_indices = [i for i in range(len(self.text)) if self.text[i] in self.core_concepts]
        self.mutable_indices = [i for i in range(len(self.text)) if not self.text[i] in self.core_concepts]
        
        # how likely is the sentence in English language?
        self.text_plausibility = text_plausibility
        return
        
    def __hash__(self):
        return hash(to_string(self.text))
    
    def __eq__(self, other):
        return to_string(self.text) == to_string(other.text)

    def __str__(self):
        text = to_string(self.text)
        text = text[0].upper() + text[1:]
        return text

    
class Multi_Phrase_Wrapper():
    def __init__(self, search_words, device, min_length, max_length):
        
        self.search_words = search_words
        self.min_length = min_length
        self.max_length = max_length
        
        self.prompts = []
        self.word_filler = Word_Filler_Hugging_Face(top_k=1000, device=device)
        return
    
    def _filter_prompts_alphanums(self, lst, lst_type='prompts'):
        assert lst_type in ['prompts', 'strings']
        if lst_type == 'prompts': texts = [to_string(p.text) for p in lst]
        else: texts = lst
           
        return [x for i, x in enumerate(lst) if ''.join(texts[i].split()).isalnum()]
    
    def _filter_prompts_search_word(self, lst, lst_type='prompts'):
        assert lst_type in ['prompts', 'strings']
        if lst_type == 'prompts': texts = [to_string(p.text) for p in lst]
        else: texts = lst
            
        return [x for i, x in enumerate(lst) if all([x.lower() in texts[i].lower() for x in self.search_words])]
    
    def _filter_prompts_num_words(self, lst, lst_type='prompts'):
        assert lst_type in ['prompts', 'strings']
        if lst_type == 'prompts': texts = [to_string(p.text) for p in lst]
        else: texts = lst
            
        return [x for i, x in enumerate(lst) if num_words(texts[i]) >= self.min_length and \
            num_words(texts[i]) <= self.max_length]

    def _init_prompts(self, randomize_top=1):
        # for all caption lengths:
        # -- generate model captions with core words shifted along
        # -- other words start as placeholders and are gradually added left and right of search word
        captions = []
        placeholder = '-'
        
        for L in range(self.min_length, self.max_length+1):
            for core_position_a in range(L):
                for core_position_b in range(L):
                    
                    
                    if core_position_a == core_position_b: continue
                    # TODO: generalise to k fixed phrases
                    # TODO: generalise phrases of length >= 1
                    string = self.search_words[0]
                    b_string = self.search_words[1]
                    
                    for i in range(L):
                        if i == core_position_a:
                            continue
                            
                        elif i == core_position_b and i < core_position_a:
                            string = b_string + ' ' + string
                            continue
                        elif i == core_position_b and i > core_position_a:
                            string = string + ' ' + b_string
                            continue
                        elif i < core_position_a:
                            string = placeholder + ' ' + string
                            res = self.word_filler.fill(string=string, mutable_indices=[0])

                        elif i > core_position_a:
                            string = string + ' ' + placeholder
                            last_index = len(to_list(string)) - 1
                            res = self.word_filler.fill(string=string, mutable_indices=[last_index])

                        else:
                            raise NotImplementedError
                        
                        texts = list(set([x[0] for x in res]))
                        texts = [x for x in texts if not x in captions]
                        texts = self._filter_prompts_alphanums(lst=texts, lst_type='strings')
                        string = texts[0]
                    
                    captions.append(string)
           
        prompts = [Phrase(
                text = captions[i], 
                core_concepts = self.search_words) for i in range(len(captions))]
        
        for p in prompts:
            assert p.text_plausibility is None
            p.text_plausibility = 0
        
        self.prompts += prompts
        
        return prompts
        
    def _branch_out_prompt(self, prompt):  
        
        # generate all top k possibilities for every mutable index
        res = self.word_filler.fill(
            string = to_string(prompt.text), 
            mutable_indices = prompt.mutable_indices,
        )

        res = sorted(res, key=lambda x: x[1], reverse=True)
        res = [x for x in res if all([w.lower() in x[0].lower() for w in self.search_words])]

        new_prompts = []
        
        for string, score in res:
            
            new_prompt = Phrase(
                text = string,
                core_concepts = prompt.core_concepts,
                text_plausibility = score,
            ) 

            new_prompts.append(new_prompt)
        
        return new_prompts
    
    def _get_new_prompts(self, prompts, N, min_score):
        orig = list(prompts)
        n_roots = len(prompts)
        
        # iterations progressively get better
        # but also with better quality text, there are more collisions
        touched_terms = []
        
        for iteration in range(10000):
            
            for L in range(self.min_length, self.max_length+1):
                
                # spend more iters on longer phrases as larger combinatorial space to search
                for repeat in range(L):
                    to_expand = [p for p in prompts if not to_string(p.text) in touched_terms]
                    to_expand = [p for p in to_expand if len(p.text) == L]
                    
                    to_expand = to_expand[0]
                    touched_terms.append(to_string(to_expand.text))

                    raw_prompts = self._branch_out_prompt(prompt=to_expand)
                    new_prompts = self._filter_prompts_alphanums(lst=raw_prompts, lst_type='prompts')
                    new_prompts = self._filter_prompts_num_words(lst=new_prompts, lst_type='prompts')
                    new_prompts = self._filter_prompts_search_word(lst=new_prompts, lst_type='prompts')
                    new_prompts = list(set(new_prompts))

                    # keep all even if not meeting min score
                    prompts += new_prompts
                    prompts = list(set(prompts))
                    prompts = sorted(prompts, key=lambda x: x.text_plausibility, reverse=True)    
            
            effective = [p for p in prompts if p.text_plausibility >= min_score]
            print(f'generated {100 * (len(effective) / N)}% of dataset -- {len(effective)}/{N}')
            print(f'mean effective fluency: {np.mean([p.text_plausibility for p in effective])}')
            
            if len(effective) >= N:
                break
            
            else:
                print(len(effective), N+n_roots)
                
            prompts = orig + [p for p in prompts if p.text_plausibility > 0.002]
                
        return effective
    
    def generate_dataset(self, N, min_fluency_score=0.003, init_prompts=None):
        if init_prompts is None: init_prompts = self._init_prompts()
        ds = self._get_new_prompts(prompts=init_prompts, N=N, min_score=min_fluency_score)
        return ds
