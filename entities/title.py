from fuzzywuzzy import fuzz



class TitleBase:
    def __init__(self, names: list, **kwargs):
        raise NotImplemented
    
    def __eq__(self, other):
        raise NotImplemented
    
    def strong_equal_names_n(self, other):
        raise NotImplemented


        
class Title(TitleBase):
    def __init__(self, names: list, meta=None):
        self.names = list(set(names))
        self.meta = meta
    
    def _clear(self, s):
        s = ''.join(list(filter(lambda c: c.isalpha() or c.isdigit() or c == ' ', s)))
        s = s.lower()
        return s
        
    def _fuzzy_equal(self, s1, s2):
        return self._clear(str(s1)) == self._clear(str(s2))
        
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
    
    def get_index(self):
        try:
            return self.meta['index']
        except:
            return None
    
    def __repr__(self):
        return "<Title> with names " + ', '.join(list(map(str, self.names)))

    

class FuzzyTitle(TitleBase):
    def __init__(self, names: list, meta=None):
        names = list(filter(lambda name: isinstance(name, str), names))
        self.names = list(set(names))
        self.meta = meta

    def __eq__(self, other):
        for name1 in self.names:
            for name2 in other.names:
                if fuzz.token_sort_ratio(name1.lower(), name2.lower()) >= 75:
                    return True
        return False

    def strong_equal_names_n(self, other):
        max_similarity = 0
        for name1 in self.names:
            for name2 in other.names:
                sim = fuzz.partial_token_set_ratio(name1.lower(), name2.lower())
                if sim > max_similarity:
                    max_similarity = sim
        return max_similarity

    def get_index(self):
        try:
            return self.meta['index']
        except:
            return None

    def __repr__(self):
        return "<Title> with names " + ', '.join(list(map(str, self.names)))
