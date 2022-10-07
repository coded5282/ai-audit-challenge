import numpy as np
from transformers import pipeline

class Classifier():
    def __init__(self, device):
        self.device = device
        return
    
    def predict(self, lst_texts):
        ''' should return a K x len(lst_texts) array of probabilities'''
        raise NotImplementedError
    
class Sentiment_Classifier(Classifier):
    def __init__(self, device, batch_size):
        super().__init__(device=device)
        
        kwargs = {
            'task' : 'sentiment-analysis', 
            'model' : "cardiffnlp/twitter-roberta-base-sentiment", 
            'batch_size' : batch_size,
            'return_all_scores': True
        }
        
        if self.device != 'cpu':
            if type(self.device) == type(0):
                kwargs['device'] = self.device
            elif self.device == 'cuda':
                kwargs['device'] = 0
            else:
                raise NotImplementedError
            
        self.classifier = pipeline(**kwargs)
        return
    
    def predict(self, lst_texts):
        res = self.classifier(lst_texts)
        assert len(res) == len(lst_texts)
        
        arrs = []
        for lst in res:
            arr = np.zeros((3, 1))
            
            for dct in lst:
                idx = int(dct['label'].split("LABEL_")[-1]) 
                assert idx in [0, 1, 2]
                arr[idx, 0] = dct['score']
            
            assert abs(1 - arr.sum()) < 1e-3
            arrs.append(arr)
           
        arrs = np.concatenate(arrs, axis=-1)
        assert arrs.shape == (3, len(lst_texts))
        
        return arrs
    