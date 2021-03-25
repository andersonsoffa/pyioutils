import string

_leet_map = {k: [k] for k in string.ascii_lowercase}
_leet_map.update({k: [k] for k in string.ascii_uppercase})
_leet_map.update({str(i): [str(i)] for i in range(0,10)})
_leet_map['a'].extend(['4','@'])
_leet_map['A'].extend(['4','@'])
_leet_map['i'].extend(['!', '1'])
_leet_map['I'].extend(['1','!','|'])
_leet_map['l'].extend(['1','|'])
_leet_map['o'].append('0')
_leet_map['O'].append('0')
_leet_map['s'].extend(['5', '$'])
_leet_map['S'].extend(['5', '$'])
_leet_map['t'].append('7')
_leet_map['T'].append('7')
_leet_map['e'].append('3')
_leet_map['E'].append('3')
_leet_map['0'].extend(['o', 'O'])
_leet_map['1'].extend(['I', 'i', 'l', '|'])
_leet_map['3'].extend(['E', 'e'])
_leet_map['5'].extend(['s', 'S'])

_case_map = {k: [k, k.upper()] for k in string.ascii_lowercase}
_case_map.update({k: [k, k.lower()] for k in string.ascii_uppercase})

valid_pass_chars = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ÀÁÂÃÇÉÊÍÑÚàáâãçéíñóôõú'

def gen_leet_mut(word, upto=3):
    if word:
        if upto:
            res = []        
            char = word[0]
            for c in _leet_map.get(char, char):
                res.extend([c+r for r in gen_leet_mut(word[1:], upto-1 if c != char else upto)])
            return res
        else:
           return [word] 
    return ['']


def gen_case_mut(word, upto=3):
    if word:
        if upto:
            res = []
            char = word[0]        
            for c in _case_map.get(char, char):
                res.extend([c+r for r in gen_case_mut(word[1:], upto-1 if c != char else upto)])
            return res
        else:
           return [word] 
    return ['']
