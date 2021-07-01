from fuzzywuzzy import fuzz
from collections import defaultdict


class TitleBase:
    def __init__(self, names: list, **kwargs):
        raise NotImplemented

    def __eq__(self, other):
        raise NotImplemented

    def strong_equal_names_n(self, other):
        raise NotImplemented


class ClearStringTitle(TitleBase):

    def _clear(self, s):
        s = ''.join(list(filter(
            lambda c: c.isalpha() or c.isdigit() or c == ' ', s)))
        s = s.lower()
        return s

    def _fuzzy_equal(self, s1, s2):
        return self._clear(str(s1)) == self._clear(str(s2))

    def get_index(self):
        try:
            return self.meta['index']
        except IndexError:
            return None


class CompareByLanguageOnClearStrings(ClearStringTitle):
    def __init__(self, names: list, meta=None):
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
            for key in self.names:
                for name1 in self.names[key]:
                    for name2 in other.names[key]:
                        if self._fuzzy_equal(name1, name2):
                            return True
            return False


    def strong_equal_names_n(self, other):
        eqs = 0
        for key in self.names:
            for name1 in self.names[key]:
                for name2 in other.names[key]:
                    if self._fuzzy_equal(name1, name2):
                        eqs += 1
        return eqs


class SimpleTitle(ClearStringTitle):
    def __init__(self, names: list, meta=None):
        self.names = list(set(names))
        self.meta = meta

    def __eq__(self, other):
        for name1 in self.names:
            for name2 in other.names:
                if self._fuzzy_equal(name1, name2):
                    return True
        return False

    def strong_equal_names_n(self, other):
        eqs = 0
        for name1 in self.names:
            for name2 in other.names:
                if self._fuzzy_equal(name1, name2):
                    eqs += 1
        return eqs


    def __repr__(self):
        return "<SimpleTitle> with names " + ', '.join(list(map(str, self.names)))


class FuzzyTitle(TitleBase):
    def _fuzzy_equal(self, s1, s2):
        return str(s1) == str(s2)

    def _clear(self, s):
        s = ''.join(list(filter(
            lambda c: c.isalpha() or c.isdigit() or c == ' ', s)))
        s = s.lower()
        return s

    def get_difference(self, name1, name2):
        return fuzz.token_sort_ratio(name1.lower(), name2.lower())


class CompareByLanguageTitle(FuzzyTitle):
    def __init__(self, names: list, meta=None):
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
        for key in self.names:
            for name1 in self.names[key]:
                for name2 in other.names[key]:
                    if self.get_difference(name1, name2) >= 75:
                        return True
        return False

    def strong_equal_names_n(self, other):
        eqs = 0
        for key in self.names:
            for name1 in self.names[key]:
                for name2 in other.names[key]:
                    if self._fuzzy_equal(name1, name2):
                        eqs += 1
        return eqs


class FuzzyTitleOnClearStrings(FuzzyTitle):
    def __init__(self, names: list, meta=None):
        names = list(filter(lambda name: isinstance(name, str), names))
        self.names = list(set(names))
        self.meta = meta

    def __eq__(self, other):
        for name1 in self.names:
            for name2 in other.names:
                if self.get_difference(name1, name2) >= 75:
                    return True
        return False

    def strong_equal_names_n(self, other):
        max_similarity = 0
        for name1 in self.names:
            for name2 in other.names:
                sim = self.get_difference(name1, name2)
                max_similarity = max(sim, max_similarity)

        return max_similarity

    def get_index(self):
        try:
            return self.meta['index']
        except IndexError:
            return None

    def __repr__(self):
        return "<SimpleTitle> with names " + ', '.join(list(map(str, self.names)))
