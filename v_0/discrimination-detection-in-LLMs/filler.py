from transformers import pipeline
from text_helpers import *

class Word_Filler_Hugging_Face():
    def __init__(self, top_k=10, device='cpu'):
        # ["roberta-base", "roberta-large", "bert-base-uncased"]
        assert type(top_k) == type(0)
        self.top_k = top_k
        self.device = device
        
        kwargs = {
            'task' : 'fill-mask', 
            'model' : 'roberta-large', 
            'top_k' : self.top_k,
        }
        
        if self.device != 'cpu':
            assert type(self.device) == type(0)
            kwargs['device'] = self.device
            
        self.filler = pipeline(**kwargs)
        self.mask_token="<mask>"
        return
        
    def fill(self, string, mutable_indices):
        assert type(string) == type("")
        assert type(mutable_indices) == type([])
        
        masked_strings = []
        
        for index in mutable_indices:
            
            lst = to_list(string)
            assert len(lst) > 1
            
            lst[index] = self.mask_token
            masked_strings.append(to_string(lst))
        
        model_outs = self.filler(masked_strings)
        if len(masked_strings) == 1: model_outs = [model_outs]
            
        results = [x['sequence'] for categ in model_outs for x in categ]
        scores = [round(x['score'],3) for categ in model_outs for x in categ]
        assert len(results) == len(scores) == self.top_k * len(mutable_indices)
        
        final = list(zip(results, scores))
        return [x for x in final if not x[0] == string]
        

# word_filler = Word_Filler_Hugging_Face()
# word_filler.fill("Hey how are you bro?", [0,2,4])
