import re
from datetime import timedelta

month_names = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

rx_ym = re.compile(r'(\d{1,2}|'+'[a-z]*|'.join(month_names)+r'[a-z]*'+r')([\-\/])(\d{2,4})$', re.IGNORECASE)

min_val_year = 1900
max_val_year = 2050

rx_td = re.compile(r'((?P<hours>\d+?)h[r]?)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')


def parse_time(time_str):
    parts = rx_td.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)


def isadate(dstring):
    if len(dstring) < 5 or not dstring[-1].isdigit():
        return False
    dstring = re.sub(r'\s', '', dstring)
    ymarray = rx_ym.findall(dstring)
    res = len(dstring) > 4 and len(ymarray) == 1
    if res:
        month, _, year  = ymarray[0]
        res = (len(year) > 2 and min_val_year <= int(year) <= max_val_year) or len(year) == 2
        res = res and (not month.isdigit() or 0 < int(month) < 13)
        if res:
            dia = dstring.replace(''.join(list(ymarray[0])), '')
            dia = re.sub(r'[\-\/]', '', dia)
            res = (dia == '' or (dia.isdigit() and 0 < int(dia) < 32))
    return res
    
    
class YearMonth(object):

    def __init__(self, y, m):
        self.year = y
        self.month = m

    def __repr__(self):
        return self.ymstr('{y}-{m:02d}')

    def __setattr__(self, key, value):
        if key == 'month':
            res = (self.year * 12)
            res += value
            self.year = res // 12
            if res % 12 != 0:
                value = res % 12
            else:
                self.year -= 1
                value = 12
        super().__setattr__(key, value)

    def ymstr(self, fmt='{y}{m:02d}'):
        return fmt.format(y=self.year, m=self.month)

    def __call__(self, *args, **kwargs):
        return self.year, self.month

    def __int__(self):
        return (self.year*12)+self.month

    def __copy__(self):
        res = type(self)(self.year, self.month)
        return res


'''
class YearMonthIt:

    def __init__(self, year, month=(1, 12)):
        ys, ye = force2tuple(year)
        ms, me = force2tuple(month)
        self.first = YearMonth(ys, ms)
        self.last = YearMonth(ye, me)

    def __iter__(self):
        aux = copy(self.first)

        for i in range(int(self.first), int(self.last)+1):
            yield aux.year, aux.month
            aux.month += 1

'''        