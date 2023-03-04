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