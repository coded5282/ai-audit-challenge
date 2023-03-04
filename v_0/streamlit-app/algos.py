import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class ActiveLearningAlgo(object):
    """ActiveLearningAlgo
    Given a set of vectors, allows iterative sampling. 
    Internal state gets updated with every proposed sample and the reaction to that sample.
    
    Args:
        X(np.array): a 2D array of shape (num vectors, dim embedding)
        idx2labels(dict): mapping from (a small subset of) indices of X to labels
    """
    def __init__(self, prompt_data):
        self.prompt_data = prompt_data
        return

    def update(self):
        raise NotImplementedError

    def next_sample(self, X):
        raise NotImplementedError

class RandomSampling(ActiveLearningAlgo):
    def __init__(self, prompt_data):
        super().__init__(prompt_data)

    def update(self):
        pass

    def next_sample(self):
        return np.random.choice(len(self.prompt_data))

class EmbeddingsSampling(ActiveLearningAlgo):
    def __init__(self, prompt_data):
        super().__init__(prompt_data)
        # self.prompt_data contains prompt embeddings
        self.selected_idxs = []

    def update(self, idx):
        self.selected_idxs.append(idx)

    def next_sample(self):
        sims = cosine_similarity(self.prompt_data[self.selected_idxs], Y=self.prompt_data, dense_output=True)
        sims = sims.sum(axis=0)
        order = sims.argsort()
        order = [x for x in order if not x in self.selected_idxs]
        next_idx = order[0]
        return next_idx
    
class CurveFittingAlgo(object):
    """CurveFittingAlgo
    Given a large set of vectors with a small subset carrying categorical labels, 
    propagate the labels across the large set
    
    Args:
        X(np.array): a 2D array of shape (num vectors, dim embedding)
        idx2labels(dict): mapping from (a small subset of) indices of X to labels
        
    Note: Labels are tuples (label, subgroup_string)
    """
    def __init__(self, X):
        self.X = X
        # self.idx2labels = idx2labels
        pass

    def fit_and_predict(self):
        raise NotImplementedError

class CosineSimFit(CurveFittingAlgo):
    def __init__(self, X):
        # super().__init__(X, idx2labels)
        super().__init__(X)
        return
    
    def fetch_neighborhood(self, src_idx, min_cos_sim):
        """helper for the required fit_and_predict method"""
        sims = cosine_similarity(self.X[src_idx:src_idx+1], Y=self.X, dense_output=True)[0]
        mask = sims >= min_cos_sim
        nbrs = np.argwhere(mask)[:,0]
        nbrs = [int(idx) for idx in nbrs if idx != src_idx]
        return nbrs

    def fit_and_predict(self, label_of_interest, subgroup_of_interest, min_cos_sim, idx2labels):
        """
        given a binary label L of interest (int) and a subgroup of interest (string)
        fetches the neighborhood around every point with label L for that subgroup
        excludes points that fall in the neighborhood of other (label, subgroup) pairs
        returns a master list of all points to which label (L, subgroup_of_interest) was 'propagatable'
        """
        self.idx2labels = idx2labels
        # included idxs
        idxs_interest = [idx for idx in self.idx2labels if self.idx2labels[idx][0]==label_of_interest]
        idxs_interest = [idx for idx in idxs_interest if self.idx2labels[idx][1]==subgroup_of_interest]
        
        interest_nbrhds = [self.fetch_neighborhood(idx, min_cos_sim) for idx in idxs_interest]
        
        # excluded idxs
        idxs_composite = [idx for idx in self.idx2labels if not idx in idxs_interest]
        assert len(idxs_interest) + len(idxs_composite) == len(self.idx2labels)

        composite_nbrhds = [self.fetch_neighborhood(idx, min_cos_sim) for idx in idxs_composite]
        
        # flatten idxs to exclude
        all_composite_idxs = list(set([x for lst in composite_nbrhds for x in lst]))

        # return idxs of interest still grouped by cluster
        # idxs_of_interest_clustered = [[ele for ele in sub if ele not in all_composite_idxs] for sub in interest_nbrhds]
        # return idxs_interest, idxs_of_interest_clustered
        return idxs_interest, interest_nbrhds