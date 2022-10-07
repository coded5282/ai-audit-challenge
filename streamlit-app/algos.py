import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class ActiveLearningAlgo(object):
    def __init__(self):
        pass

    def update(self):
        raise NotImplementedError

    def next_sample(self, X):
        raise NotImplementedError

class RandomSampling(ActiveLearningAlgo):
    def __init__(self, prompt_data):
        super().__init__()
        self.prompt_data = prompt_data

    def update(self):
        pass

    def next_sample(self):
        return np.random.choice(len(self.prompt_data))

class EmbeddingsSampling(ActiveLearningAlgo):
    def __init__(self, prompt_data):
        super().__init__()
        self.prompt_data = prompt_data # prompt embeddings
        self.selected_idxs = [0]

    def update(self, idx):
        self.selected_idxs.append(idx)

    def next_sample(self):
        sims = cosine_similarity(self.prompt_data[self.selected_idxs], Y=self.prompt_data, dense_output=True)
        sims = sims.sum(axis=0)
        order = sims.argsort()
        order = [x for x in order if not x in self.selected_idxs]
        next_idx = order[0]
        return next_idx