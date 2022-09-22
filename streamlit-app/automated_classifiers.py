# imports
import numpy as np
from transformers import pipeline
import torch
from detoxify.detoxify import get_model_and_tokenizer

DOWNLOAD_URL = "https://github.com/unitaryai/detoxify/releases/download/"
MODEL_URLS = {
    "original": DOWNLOAD_URL + "v0.1-alpha/toxic_original-c1212f89.ckpt",
    "unbiased": DOWNLOAD_URL + "v0.3-alpha/toxic_debiased-c7548aa0.ckpt",
    "multilingual": DOWNLOAD_URL + "v0.4-alpha/multilingual_debiased-0b549669.ckpt",
    "original-small": DOWNLOAD_URL + "v0.1.2/original-albert-0e1d6498.ckpt",
    "unbiased-small": DOWNLOAD_URL + "v0.1.2/unbiased-albert-c8519128.ckpt",
}
PRETRAINED_MODEL = None

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

class Detoxify:
    """Detoxify
    Easily predict if a comment or list of comments is toxic.
    Can initialize 5 different model types from model type or checkpoint path:
        - original:
            model trained on data from the Jigsaw Toxic Comment
            Classification Challenge
        - unbiased:
            model trained on data from the Jigsaw Unintended Bias in
            Toxicity Classification Challenge
        - multilingual:
            model trained on data from the Jigsaw Multilingual
            Toxic Comment Classification Challenge
        - original-small:
            lightweight version of the original model
        - unbiased-small:
            lightweight version of the unbiased model
    Args:
        model_type(str): model type to be loaded, can be either original,
                         unbiased or multilingual
        checkpoint(str): checkpoint path, defaults to None
        device(str or torch.device): accepts any torch.device input or
                                     torch.device object, defaults to cpu
        huggingface_config_path: path to HF config and tokenizer files needed for offline model loading
    Returns:
        results(dict): dictionary of output scores for each class
    """

    def __init__(self, model_type="original", checkpoint=PRETRAINED_MODEL, device="cpu", huggingface_config_path=None, model_dir=None):
        super().__init__()
        self.model, self.tokenizer, self.class_names = load_checkpoint(
            model_type=model_type,
            checkpoint=checkpoint,
            device=device,
            huggingface_config_path=huggingface_config_path,
            model_dir=model_dir if not None else torch.hub.get_dir(),
        )
        self.device = device
        self.model.to(self.device)

    @torch.no_grad()
    def predict(self, text):
        self.model.eval()
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(self.model.device)
        out = self.model(**inputs)[0]
        scores = torch.sigmoid(out).cpu().detach().numpy()
        results = {}
        for i, cla in enumerate(self.class_names):
            results[cla] = (
                scores[0][i] if isinstance(text, str) else [scores[ex_i][i].tolist() for ex_i in range(len(scores))]
            )
        return results

# https://huggingface.co/unitary/toxic-bert
    
class Toxicity_Classifier(Classifier):
    def __init__(self, device, model_type='original', model_dir=None): # unbiased, multilingual
        super().__init__(device=device)
        
        kwargs = {
            'model_type' : model_type,
            'model_dir' : model_dir
        }
        
        if self.device != 'cpu':
            assert type(self.device) == type(0) or self.device == 'cuda'
            kwargs['device'] = 'cuda'
            
        self.classifier = Detoxify(**kwargs)
        return
    
    def predict(self, lst_texts):
        keys = ['toxicity', 'severe_toxicity', 'obscene', 'threat', 'insult', 'identity_attack']
        res = self.classifier.predict(lst_texts)
        pred = np.stack([res[k] for k in keys], axis=0)
        assert pred.shape == (len(keys), len(lst_texts))
        return pred
    
def load_checkpoint(model_type="original", checkpoint=None, device="cpu", huggingface_config_path=None, model_dir=None):
    if checkpoint is None:
        checkpoint_path = MODEL_URLS[model_type]
        loaded = torch.hub.load_state_dict_from_url(checkpoint_path, model_dir=model_dir, map_location=device)
    else:
        loaded = torch.load(checkpoint, model_dir=model_dir, map_location=device)
        if "config" not in loaded or "state_dict" not in loaded:
            raise ValueError(
                "Checkpoint needs to contain the config it was trained \
                    with as well as the state dict"
            )
    class_names = loaded["config"]["dataset"]["args"]["classes"]
    # standardise class names between models
    change_names = {
        "toxic": "toxicity",
        "identity_hate": "identity_attack",
        "severe_toxic": "severe_toxicity",
    }
    class_names = [change_names.get(cl, cl) for cl in class_names]
    model, tokenizer = get_model_and_tokenizer(
        **loaded["config"]["arch"]["args"],
        state_dict=loaded["state_dict"],
        huggingface_config_path=huggingface_config_path,
    )

    return model, tokenizer, class_names

def get_auto_classifier(evaluation_metric):
    MODEL_DIR = '/dfs/scratch0/edjchen/temp/'
    device_c = 'cpu'
    if evaluation_metric == 'Toxicity':
        c = Toxicity_Classifier(device=device_c, model_type='original', model_dir=MODEL_DIR)
    elif evaluation_metric == 'Sentiment':    
        c = Sentiment_Classifier(device=device_c, batch_size=10)
    return c