# -*- coding: utf-8 -*- 
__author__ = 'anderson.soffa'
import pyperclip
#from striprtf.striprtf import rtf_to_text


def clp2lst():
    raw = pyperclip.paste()
    if raw:
        raw = raw.split('\r\n' if '\r\n' in raw else '\n')
        return raw[:-1] if raw[-1] == '' else raw
    return None


def lst2clp(itemlist, lend='\n'):
    pyperclip.copy(lend.join(map(lambda row: row if isinstance(row, str) else str(row), itemlist)))


def clpdatasettolist(sep, ncols):
    data = pyperclip.paste().split(sep)
    raw = [data[x:x+ncols] for x in range(0, len(data), ncols)]
    def clean(v):
        aux = v.strip('\r\n').strip('\t').strip()
        if aux.isdigit():
            return aux
        else:
            if aux[:5] == '{\\rtf':
               #aux = rtf_to_text(aux) 
               raise Exception('Need to install striprtf in order to process RTF content')
                
            if aux[:1] == '\r':
                aux = aux[1:]
            if aux[:1] == '\n':
                aux = aux[1:]
            if aux[:1] == '\t':
                aux = aux[1:]
                
            return aux.replace('\r\n','<nl>').replace('\t',' ')    
    return [list(map(clean, l)) for l in raw]

    
'''    
def patinlist(data, rx, gindex=0):
    mt = [ [ri, [[ci, f] for ci, c in enumerate(r) for f in rx.findall(c) if f.strip() != '']] for ri, r in enumerate(data)]
    mt = [ l for l in mt if len(l[1])>0 ]
    mt = [ [l[0], ci, ' | '.join(re.findall('.{1,50}'+v+'.{1,50}', data[l[0]][ci]))] for l in mt for ci, v in l[1] ]
    return mt
'''


