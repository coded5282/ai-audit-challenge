import datetime

def time_now():
    string = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")    
    return '_'.join(string.split(' ')).replace('/', '_')


import matplotlib.pyplot as plt

def scatter_across_epochs(y, y_label, title):
    x = list(range(len(y)))
    plt.scatter(x, y)
    plt.xlabel('epochs')
    plt.ylabel(y_label)
    plt.title(title)
    plt.show()
    return

from torch.utils.data import Dataset

# wrap HuggingFace input list in this so can see progress bar as module works on these inputs
class List_Dataset(Dataset):
    def __init__(self, lst):
        self.lst = lst
    def __len__(self):
        return len(self.lst)

    def __getitem__(self, i):
        return self.lst[i]

def reduce_texts_to_phrases(texts):
    
    def apply_fn_to_lst_elts(lst, fn):
        new = []
        for x in lst:
            res = fn(x)
            assert type(res) == type([])
            for x in res: assert type(x) == type("")
            new += res
        return new

    def garbage_collect(lst):
        lst = [x for x in lst if len(x) > 5]
        return lst

    texts = apply_fn_to_lst_elts(texts, lambda x: x.split('\n'))
    texts = apply_fn_to_lst_elts(texts, lambda x: x.split('•'))
    texts = apply_fn_to_lst_elts(texts, lambda x: x.split('  '))
    texts = apply_fn_to_lst_elts(texts, lambda x: [''] if any(c.isdigit() for c in x) else [x])
    texts = apply_fn_to_lst_elts(texts, lambda x: [''.join([c for c in x[:5] if not (c in '-')])+x[5:]])
    texts = apply_fn_to_lst_elts(texts, lambda x: [''.join([c for c in x[:5] if not (c in '+)(#$%&0123456789')])+x[5:]])
    texts = apply_fn_to_lst_elts(texts, lambda x: [x.strip()])
    texts = garbage_collect(texts)
    return texts