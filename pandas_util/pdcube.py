import pandas as pd
from collections import namedtuple
Cond = namedtuple('Cond', ['query', 'colname', 'fdict'])


def gencube(df, indcol, group, *cond):
    def gendf(qry, colname, fdict):
        ret = df.query(qry).groupby(group, as_index=False).agg({colname: [k for k, v in fdict.items()]})
        for k, v in fdict.items():
            ret[v] = ret[colname][k]
        ret.columns = ret.columns.droplevel(1)
        return ret.drop(columns=colname)

    res = None
    for col in cond:
        if res is None:
            res = gendf(col.query, col.colname, col.fdict)
        else:
            res = pd.merge(res, gendf(col.query, col.colname, col.fdict), left_on=indcol, right_on=indcol, how='outer' )
    return res


#def gencube(df, indcol, *cond):
#    return gencube(df, indcol, indcol, *cond)
