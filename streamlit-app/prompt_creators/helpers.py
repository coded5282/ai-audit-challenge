import numpy as np
import os
os.environ['TRANSFORMERS_CACHE'] = '/dfs/scratch0/edjchen/'
from transformers import pipeline, AutoConfig
from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer

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
            # 'model' : "cardiffnlp/twitter-roberta-base-sentiment", 
            'model' : "/lfs/hyperturing2/0/edjchen/temp/sentiment",
            'batch_size' : batch_size,
            'return_all_scores': True,
            # 'pretrained_model_name_or_path': '/lfs/hyperturing1/0/edjchen/temp/'
        }
        
        if self.device != 'cpu':
            if type(self.device) == type(0):
                kwargs['device'] = self.device
            elif self.device == 'cuda':
                kwargs['device'] = 0
            else:
                raise NotImplementedError
        
        # model = AutoConfig.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment", cache_dir='/lfs/hyperturing1/0/edjchen/temp/')
        # _ = pipeline("sentiment-analysis", model=model, batch_size=batch_size, return_all_scores=True)
        # tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment", cache_dir='/dfs/scratch0/edjchen/', force_download=True)
        # model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")

        # tokenizer = AutoTokenizer.from_pretrained("/lfs/hyperturing1/0/edjchen/temp/sentiment")
        # self.classifier = AutoModelForSequenceClassification.from_pretrained("/lfs/hyperturing1/0/edjchen/temp/sentiment")

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
    