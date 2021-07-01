from typing import List
from .simpletitle import TitleBase


class Matcher:
    def __init__(self, titles: List[TitleBase, ]):
        raise NotImplemented

    def find_matches(self, gtitle: TitleBase) -> list:
        raise NotImplemented


class FullMatcher(Matcher):
    """class with multithread access to data and public method
                                          for comparing titles"""

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
        eps_diff = 3  # of 100
        matched = []

        for j, mtitle in enumerate(self.titles):
            if mtitle == gtitle:
                return [mtitle]
        return []
