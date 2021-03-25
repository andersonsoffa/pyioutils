# -*- coding: utf-8 -*- 
__author__ = 'anderson.soffa'
import re
import string
import unicodedata
from functools import reduce
from collections import Counter

month_names = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

_accents = {u'á': 'a', u'à': 'a', u'ã': 'a', u'â': 'a', u'Á': 'A', u'Ã': 'A', u'Â': 'A', u'À': 'A', u'ç': 'c',
            u'Ç': 'C', u'ó': 'o', u'õ': 'o', u'ô': 'o', u'é': 'e', b'\xcc\x81': "'", b'e\xcc\x81': 'e',
            b'\xc3\xa9\xcc\x81': 'e', u'É': 'E', u'Ê': 'E', u'í': 'i', u'Í': 'I', u'ú': 'u', u'Ú': 'U'}


_valid_chars = string.printable[:-5]
_valid_chars += ''.join([v for v in _accents.keys() if type(v)==str])


class WordParser(object):
    _ds = u'áàãâÁÃÂÀçÇóõôéêÉÊíÍúÚ'
    rxtkn = re.compile(f'[^a-z0-9{_ds}]+', re.IGNORECASE)

    def __init__(self, to_lower=False):
        self.caseLower = to_lower

    def word_list(self, text):
        if not text:
            return []
        res = self.rxtkn.split(text)
        if self.caseLower:
            res = [v.lower() for v in res]
        return res

    def word_count(self, text, unique=False):
        if unique:
            return len(self.word_set(text))
        else:
            return len(self.word_list(text))

    def word_set(self, text):
        return set(self.word_list(text))


def strip_accents(text):
    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")
    return str(text)


def strip_extra_spaces(text, replace_by=' '):
    return re.sub(r'\s+', replace_by, text)


def remove_accent(l):
    return strip_accents(l)
    # return ''.join([_accents.get(x, _accents.get(x.encode(), x)) for x in l])


def remove_accent_upper(l):
    return remove_accent(l).upper()


def remove_stop_words(l, stop_words):
    return ' '.join([w for w in l.split(' ') if w not in stop_words])


def make_named_id(name, rmv=r'[\(\)\$%\'\"\.]+', accent_method=remove_accent_upper):
    if rmv:
        name = re.sub(rmv, '', name)
    name = re.sub(r'[ ]+', '_', name).strip('_').strip()
    tkns = accent_method(name).split(' ')
    res = '_'.join(filter(lambda v: len(v) > 2, tkns))
    if not res:
        res = '_'.join(tkns)
    return res


class SentenceRanker(object):

    def __init__(self, sent_list):
        self.cnt_dict = Counter([word for sent in sent_list for word in sent.split(' ')])
        self.cnt_size = len(self.cnt_dict)

    def gen_rank_tuple(self, tokens, *args):
        tkn_list = [tokens[i] for i in args]
        return ' '.join(tkn_list), reduce((lambda x, y: (self.cnt_dict[x]/self.cnt_size) * (self.cnt_dict[y]/self.cnt_size)), tkn_list)

    def gen_ranked_combinations(self, sent, *args):
        tokens = sent.split(' ')
        return [self.gen_rank_tuple(tokens, *tkn_positions) for tkn_positions in args]
        

class NameRanker(SentenceRanker):

    _tkn_pos = [(0, -1), (0, 1), (1, -1)]
    
    def gen_name_rank_list(self, name):
        return self.gen_ranked_combinations(name, *NameRanker._tkn_pos) 

    def gen_uncommon_var(self, name):
        aux = sorted(self.gen_name_rank_list(name), key=lambda tpl: tpl[1])
        return aux[0]
        
    def gen_rank_dict(self, nm_list):#, ftrans=None):
        #if ftrans:
        #    nm_list = [ftrans[nm] for nm in nm_list]
       return {nm:sorted([rank_tpl for rank_tpl in self.gen_name_rank_list(nm) if rank_tpl[1] >0]) for nm in nm_list}


def levenshtein(seq1, seq2):
    if 'np' not in globals() or globals()['np'].__name__ != 'numpy':
        import numpy as np

    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros((size_x, size_y))
    for x in range(size_x):
        matrix[x, 0] = x
    for y in range(size_y):
        matrix[0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x - 1] == seq2[y - 1]:
                matrix[x, y] = min(
                    matrix[x - 1, y] + 1,
                    matrix[x - 1, y - 1],
                    matrix[x, y - 1] + 1
                )
            else:
                matrix[x, y] = min(
                    matrix[x - 1, y] + 1,
                    matrix[x - 1, y - 1] + 1,
                    matrix[x, y - 1] + 1
                )
    return matrix[size_x - 1, size_y - 1]
