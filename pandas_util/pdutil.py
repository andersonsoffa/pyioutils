# -*- coding: utf-8 -*-
__author__ = 'anderson.soffa'
from pandas.core.frame import DataFrame
from datetime import date
import pyperclip


def cond_exp_func(cond, ref_val):
    def _is_greater(x): return x > ref_val
    def _is_equal(x): return x == ref_val
    def _is_less(x): return x < ref_val
    def _is_less_equal(x): return x <= ref_val
    def _is_greater_equal(x): return x >= ref_val
    case = {'gt': _is_greater, 'lt': _is_less, 'eq': _is_equal, 'le': _is_less_equal, 'ge': _is_greater_equal}
    return case[cond]


def freq(pd_serie, value=1, cond='gt'):
     comp_func = cond_exp_func(cond, value)
     res = pd_serie.value_counts().loc[comp_func]
     return pd_serie.isin(res.index)


def gsum(self, sumcol, group=None):
    if group:
        group = group if isinstance(group, list) else group.split(',')
        res = self.groupby(group, as_index=False)[sumcol].sum()
    else:
        res = self[sumcol].sum()
    return res


def sort(self, sortby, asc=True, top=None):
    sortby = sortby if isinstance(sortby, list) else sortby.split(',')
    if top:
        return self.sort_values(sortby, ascending=asc).head(top)
    else:
        return self.sort_values(sortby, ascending=asc)


def gtop(self, group, limit=5, asc=False):
    group = group if isinstance(group, list) else group.split(',')
    return self.sort(group, asc).groupby(group[:-1]).head(limit)


def dttimetodate(self, datetimecol, newcol=None, default=date(1900, 1, 1)):
    if newcol is not None:
        self[newcol] = self[datetimecol]
        datetimecol = newcol
    mt = self[datetimecol].astype(object).as_matrix()
    self[datetimecol] = [date(year=e.year, month=e.month, day=e.day) if e == e else default for e in mt]


def top(self, limit=5, bycol=None, asc_order=False):
    if bycol:
        return self.sort(bycol, asc=asc_order, top=limit)
    else:
        return self.head(limit)


def topsum(self, sumcol, group=None, bygrp=False, asc=False, limit=5):
    res = self.gsum(sumcol, group)
    if group:
        group = group if isinstance(group, list) else group.split(',')
        if bygrp:
            res = res.sort(group[:-1]+[sumcol], asc=asc).groupby(group[:-1])
        else:
            res = res.sort(sumcol, asc=asc)
    else:
        return res
    return res.head(limit)


def appendacc(self, col, start=None, breakby=[], func=None):

    acc_col = col+'_ACC'
    start = start if start else 0.0

    def _sum(prev, cur):
        if prev is not None:
            return self.loc[prev, acc_col]+self.loc[cur, col]
        else:
            return start+self.loc[cur, col]

    breakby = breakby if isinstance(breakby, list) else breakby.split(',')

    func = func if func else _sum
    self[acc_col] = 0.0

    prevrow = None
    oldkey = ''
    for i in self.index:
        curkey = '_'.join([str(self.loc[i, c]) for c in breakby])
        if curkey != oldkey:
            prevrow = None
            oldkey = curkey

        self.loc[i, acc_col] = func(prevrow, i)
        prevrow = i


def main_cols(self):
    if self._metadata and 'mcols' in self._metadata:
        #TODO: move to the cloning mechanism
        res = self[self._metadata['mcols']]
        res._metadata = self._metadata
        return res
    else:
        return self


def set_default_index(self):
    self.index = self[self._metadata['pk']]


def csv(self, file='output.csv'):
    self.to_csv(file, sep='\t', decimal=',')


def clp(self):
    clpfile = 'clipboard.temp'
    self.csv(clpfile)
    with open(clpfile, encoding='utf') as f:
        pyperclip.copy(f.read())


def patch_pandas():
    DataFrame.gsum = gsum
    DataFrame.gtop = gtop
    DataFrame.sort = sort
    DataFrame.topsum = topsum
    DataFrame.appendacc = appendacc
    DataFrame.csv = csv
    DataFrame.clp = clp
    DataFrame.dttimetodate = dttimetodate
    DataFrame.get_mcols = main_cols
    DataFrame.set_pk_idx = set_default_index
    #pandas.io.pytables.DataFrame = PDataFrame

