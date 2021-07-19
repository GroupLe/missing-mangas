from fuzzywuzzy import fuzz
from collections import defaultdict
from typing import Callable, Tuple, Union, List
import pandas as pd
from catboost import CatBoostClassifier


class TitleBase:
    def __init__(self, names: list, meta=None, **kwargs):
        raise NotImplemented

    def _compare_strings(self, s1: str, s2: str) -> bool:
        raise NotImplemented

    def __eq__(self, other):
        raise NotImplemented

    def strong_equal_names_n(self, other):
        raise NotImplemented

    def _clear(self, s: str) -> str:
        s = ''.join(list(filter(lambda c: c.isalpha() or c.isdigit() or c == ' ', s)))
        s = s.lower()
        return s

    def get_index(self):
        try:
            return self.meta['index']
        except (KeyError, AttributeError):
            return None

    @staticmethod
    def check_names(Title_first, other):
        for Title_second in other:
            if pd.isna(Title_second):
                return False
            for name in Title_second.names:
                if name not in Title_first.names:
                    return False
        return True


class CompareByLanguageTitle(TitleBase):

    def __init__(self, names: list, meta=None):
        names = list(filter(lambda name: isinstance(name, str), names))
        self.meta = meta
        self.names = defaultdict(list)
        for elem in names:
            clear_elem = self._clear(elem)
            self.names[self.get_type_name(clear_elem)].append(clear_elem)

    def get_type_name(self, name: str) -> str:
        ord_of_symbols = [ord(x) for x in filter(str.isalpha, name)]
        if len(ord_of_symbols) == 0:
            return None
        stat = sum(ord_of_symbols) / len(ord_of_symbols)
        if 65 <= stat <= 122:
            return "english"
        elif 1072 <= stat <= 1105:
            return "russian"
        else:
            return "other"

    def __eq__(self, other: TitleBase) -> bool:
        for lang in self.names.keys():
            for name1 in self.names[lang]:
                for name2 in other.names[lang]:
                    if self._compare_strings(name1, name2):
                        return True
        return False

    def strong_equal_names_n(self, other: TitleBase) -> int:
        eqs = 0
        for key in self.names:
            for name1 in self.names[key]:
                for name2 in other.names[key]:
                    if self._compare_strings(name1, name2):
                        eqs += 1
        return eqs

    @staticmethod
    def check_names(Title_first, other):
        for Title_second in other:
            if pd.isna(Title_second):
                return False
            for lang in Title_first.names:
                for name in Title_second.names[lang]:
                    if name not in Title_first.names[lang]:
                        return False
        return True


class CompareJustTitle(TitleBase):
    def __init__(self, names: list, meta=None):
        self.names = list(map(self._clear, set(str(name) for name in names)))
        self.meta = meta

    def _clear(self, s:str) -> str:
        s = ''.join(list(filter(lambda c: c.isalpha() or c.isdigit() or c == ' ', s)))
        s = s.lower()
        return s

    def __eq__(self, other: TitleBase) -> bool:
        for name1 in self.names:
            for name2 in other.names:
                if self._compare_strings(name1, name2) > 85:
                    return True
        return False

    def strong_equal_names_n(self, other) -> int:
        eqs = 0
        for name1 in self.names:
            for name2 in other.names:
                if self._compare_strings(name1, name2) > 85:
                    eqs += 1
        return eqs

    def get_index(self):
        try:
            return self.meta['index']
        except:
            return None

    def __repr__(self):
        return "<Title> with names " + ', '.join(list(map(str, self.names)))


class AbstractFuzzyComparableTitle:
    def _compare_strings(self, s1: str, s2: str) -> float:
        return fuzz.token_sort_ratio(s1.lower(), s2.lower())


class AbstractNaiveComparableTitle:
    def _compare_strings(self, s1: str, s2: str) -> float:
        return self._clear(s1.lower()) == self._clear(s2.lower())


class CompareByLanguageFuzzyTitle(AbstractFuzzyComparableTitle, CompareByLanguageTitle):
    pass


class CompareByLanguageNaiveTitle(AbstractNaiveComparableTitle, CompareByLanguageTitle):
    pass


class CompareJustFuzzyTitle(AbstractFuzzyComparableTitle, CompareJustTitle):
    pass


class CompareJustNaiveTitle(AbstractNaiveComparableTitle, CompareJustTitle):
    pass


class CompareByLanguageCatBoostTitle(CompareByLanguageTitle):
    _model = CatBoostClassifier().load_model("model_data/cat-boost-weights_depth_3.cbm", )

    @staticmethod
    def predict_batch(batch: List[List[float]]) -> List[Tuple[float, float]]:
        """Takes batch of features, returns batch of predictions"""
        return CompareByLanguageCatBoostTitle._model.predict_proba(batch)

    def __init__(self, names: list, meta=None):
        super().__init__(names, meta)

    def make_features(self, other: CompareByLanguageTitle) -> List[float]:
        """Creates features for pairs of same language names of two titles"""
        features = []
        for lang in ['russian', 'english']:
            if len(self.names[lang]) and len(other.names[lang]):
                s1, s2 = self.names[lang][0], other.names[lang][0]
                features_lang = [fuzz.ratio(s1, s2), self.is_equal(s1, s2), self.chars_jaccard(s1, s2)]
            else:
                features_lang = [-1, -1, -1]
            features += features_lang
        return features

    @staticmethod
    def is_equal(s1, s2) -> int:
        return int(s1 == s2)

    @staticmethod
    def chars_jaccard(s1, s2) -> float:
        s1, s2 = set(s1), set(s2)
        return len(s1.intersection(s2)) / len(s1.union(s2))