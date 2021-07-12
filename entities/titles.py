from fuzzywuzzy import fuzz
from collections import defaultdict


LIMIT = 0.95


class TitleBase:
    def __init__(self, names: list, **kwargs):
        raise NotImplemented

    def _compare_strings(self, s1: str, s2: str) -> bool:
        raise NotImplemented

    def __eq__(self, other):
        raise NotImplemented

    def strong_equal_names_n(self, other):
        raise NotImplemented


class CompareByLanguageTitle(TitleBase):

    def __init__(self, names: list, meta = None):
        names = list(filter(lambda name: isinstance(name, str), names))
        self.meta = meta
        self.names = defaultdict(list)
        for elem in names:
            clear_elem = self._clear(elem)
            self.names[self.get_type_name(clear_elem)].append(clear_elem)

    def get_type_name(self, name):
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

    def __eq__(self, other):
        for lang in self.names.keys():
            for name1 in self.names[lang]:
                for name2 in other.names[lang]:
                    if self._compare_strings(name1, name2) >= LIMIT:
                        return True
        return False

    def strong_equal_names_n(self, other):
        eqs = 0
        for key in self.names:
            for name1 in self.names[key]:
                for name2 in other.names[key]:
                    if self._compare_strings(name1, name2):
                        eqs += 1
        return eqs

    def _clear(self, s):
        s = ''.join(list(filter(lambda c: c.isalpha() or c.isdigit() or c == ' ', s)))
        s = s.lower()
        return s

    def get_index(self):
        try:
            return self.meta['index']
        except:
            return None


class CompareJustTitle(TitleBase):
    def __init__(self, names: list, meta=None):
        self.names = list(map(self._clear, set(str(name) for name in names)))
        self.meta = meta

    def _clear(self, s):
        s = ''.join(list(filter(lambda c: c.isalpha() or c.isdigit() or c == ' ', s)))
        s = s.lower()
        return s

    def __eq__(self, other):
        for name1 in self.names:
            for name2 in other.names:
                if self._compare_strings(name1, name2) >= LIMIT:
                    return True
        return False

    def strong_equal_names_n(self, other):
        eqs = 0
        for name1 in self.names:
            for name2 in other.names:
                if self._compare_strings(name1, name2):
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
    def _compare_strings(self, s1, s2):
        return fuzz.token_sort_ratio(s1.lower(), s2.lower())


class AbstractNaiveComparableTitle:
    def _compare_strings(self, s1, s2):
        return self._clear(s1.lower()) == self._clear(s2.lower())


class CompareByLanguageFuzzyTitle(AbstractFuzzyComparableTitle, CompareByLanguageTitle):
    pass


class CompareByLanguageNaiveTitle(AbstractNaiveComparableTitle, CompareByLanguageTitle):
    pass


class CompareJustFuzzyTitle(AbstractFuzzyComparableTitle, CompareJustTitle):
    pass


class CompareJustNaiveTitle(AbstractNaiveComparableTitle, CompareJustTitle):
    pass


