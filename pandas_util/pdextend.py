import os
import pandas as pd

from pyioutils.file_util import wait_file_lock
from pyioutils.pandas_util.pdutil import cond_exp_func


def make_list(obj):
    return obj if isinstance(obj, list) else [obj]


@pd.api.extensions.register_dataframe_accessor("append_to_file")
class LockFileAppend(object):

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def __call__(self, file_name, time_out=10, check_freq=0.1):
        tmp_file = file_name+'.lock'
        wait_file_lock(tmp_file, time_out, check_freq)
        try:
            if os.path.isfile(file_name):
                pd.read_pickle(file_name).append(self._obj).to_pickle(file_name)
            else:
                self._obj.to_pickle(file_name)
        finally:
            os.remove(tmp_file)


@pd.api.extensions.register_dataframe_accessor("as_dict")
class DataFrameToDict(object):

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def __call__(self, key='', cols=[]):
        cols = make_list(cols) or list(self._obj.columns)
        key = key or self._obj.index.name

        if not isinstance(cols, list):
            raise ValueError('Column names should be a list')
        elif key == '':
            raise ValueError('Key column is required')

        if key not in cols:
            cols.append(key)

        return pd.DataFrame(self._obj[cols]).set_index(key).to_dict(orient='index')


@pd.api.extensions.register_dataframe_accessor("apply_dict")
class ValueFromDict(object):

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def __call__(self, index, adict, value_names=None, column_names=None, keep_exist=False, defaults=None):
        if not isinstance(adict, dict):
            raise TypeError('Second argument must be a dictionary')
        elif not isinstance(index, str) or index not in self._obj.columns:
            raise TypeError('Index should be a column (pk or fk) and dictionary key')
        elif value_names is None and column_names is None:
            raise ValueError('You must at least inform the column names')

        value_names = make_list(value_names)
        column_names = value_names if column_names is None else make_list(column_names)
        defaults = [defaults]*len(column_names) if defaults is None or isinstance(defaults, str) else defaults

        if len(value_names) != len(column_names):
            raise ValueError('Number of dictionary values and columns must be the same')

        if isinstance(defaults, list):
            if len(defaults) != len(value_names):
                raise ValueError('Default values and number of columns must be equal')
            defaults = {v: d for v, d in zip(value_names, defaults)}

        df = self._obj
        for col, val in zip(column_names, value_names):
            if keep_exist and col in df.columns:
                df[col] = [adict.get(pk, {val: old}).get(val, old) for pk, old in df[[index, col]].values]
            else:
                df[col] = [adict.get(pk, defaults).get(val, defaults[val]) for pk in df[index].values]


@pd.api.extensions.register_series_accessor("freq")
class SeriesFrequency(object):
    """
    Return True or False whether the value count of the series matches the condition.

    Parameters
    ----------
    ref_val : number
        Reference count.
    condition : str
        gt, ge, lt, le, eq.

    Returns
    -------
    boolean
        True or False.

    Examples
    --------
    df[df.Field.freq(10)]
    df[df.Field.freq(7, 'lt')]
    """

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def __call__(self, ref_val=1, condition='gt'):
        comp_func = cond_exp_func(condition, ref_val)
        res = self._obj.value_counts().loc[comp_func]
        return self._obj.isin(res.index)


@pd.api.extensions.register_series_accessor("thist")
class SeriesTextHistogram(object):
    """
    Plot a text histogram
    """     

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def __call__(self, cols=80):

        total = self._obj.sum()
        normal = self._obj.max()
        return pd.DataFrame([{self._obj.index.name if self._obj.index.name else 'Index' : k, self._obj.name: v, 'Dist': v/total,
                              'Hist': '#'*int(cols*(v/normal))} for k, v in self._obj.items()])


@pd.api.extensions.register_series_accessor("vc")
class SeriesValueCountsAlias(object):
    """
    Alias for counting values
    """     

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def __call__(self):
        return self._obj.value_counts()


@pd.api.extensions.register_dataframe_accessor('sd')
class DataFrameSortDesc(object):
    """
    Alias for sort descending
    """     
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def __call__(self, cols):
        return self._obj.sort_values(cols, ascending=False)


@pd.api.extensions.register_series_accessor("ncs")
class CumulativeDistribution(object):
    """
    Returns a given column's normalized cum sum
    """     
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def __call__(self):
        total = self._obj.sum()
        return self._obj.cumsum()/total


@pd.api.extensions.register_dataframe_accessor('prto')
class ParetoFilter(object):
    """
    Return rows for which column's cumsum is within the percentile threshold
    """     
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def __call__(self, column, threshold=0.8, sort_data=True):
        res = self._obj.sort_values(column, ascending=False) if sort_data else self._obj
        ncs = res[column].ncs()
        return res[(ncs <= threshold)]
