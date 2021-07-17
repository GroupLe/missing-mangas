from typing import List
from .titles import TitleBase, CompareByLanguageCatBoostTitle
from tqdm import tqdm
import numpy as np


class Matcher:
    def __init__(self, titles: List[TitleBase, ]):
        raise NotImplemented

    def find_matches(self, gtitle: TitleBase) -> list:
        raise NotImplemented


class FullMatcher(Matcher):
    """
    Multithread compare of all foreign titles with one our title
    """

    def __init__(self, titles: List[TitleBase, ]):
        self.titles = titles

    def find_matches(self, gtitle):
        eps_diff = 3  # of 100
        matched = []

        for j, mtitle in enumerate(self.titles):
            if mtitle == gtitle:
                matched.append(mtitle)

        if len(matched) > 1:
            # search the most similar
            # Drop not so similar cases
            similarities = [gtitle.strong_equal_names_n(mtitle)
                            for mtitle in matched]
            top_similar = max(similarities)
            for i, sim in enumerate(similarities):
                if abs(similarities[i] - top_similar) <= eps_diff:
                    matched[i] = None

            matched = list(filter(lambda item: item is not None, matched))
        return matched


class FirstMatcher(Matcher):
    """class with multithread access to data
       and public method for comparing titles"""

    def __init__(self, titles):
        self.titles = titles

    def find_matches(self, gtitle):
        for j, mtitle in tqdm(enumerate(self.titles)):
            if mtitle == gtitle:
                return [mtitle]
        return []


class CatboostFullMatcher(FullMatcher):
    def __init__(self, titles: List[CompareByLanguageCatBoostTitle]):
        self.titles = titles

    def find_matches(self, gtitle: CompareByLanguageCatBoostTitle) -> list:
        # calc features batch
        make_features = lambda other_title: other_title.make_features(gtitle)
        features = list(map(make_features, self.titles))

        probs = CompareByLanguageCatBoostTitle.predict_batch(features)
        # drop predictions if title has one or more n/a name
        for i, feats in enumerate(features):
            if -1 in feats:
                probs[i] = np.array([probs[i][0], 0])
        # get greatest probs for both classes. Select the greatest of them
        pred_class = probs.max(axis=0).argmax()
        # select argument with higher prob in selected class
        # TODO: argsort to output topN?
        pred_ixs = probs[:, pred_class].argsort()
        matched = [self.titles[pred_ix] for pred_ix in pred_ixs[-3:]]
        return matched
