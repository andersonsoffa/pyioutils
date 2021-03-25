__author__ = 'anderson.soffa'
import os
import fnmatch
from time import sleep
import pickle
import json
from os import path


def dump_obj(fname, obj, ftype='b', as_json=False):
    as_json = as_json or fname.lower().endswith('json')
    if as_json:
        ftype = 't'
        
    with open(fname, 'w'+ftype) as f:
        if ftype == 'b':
            pickle.dump(obj, f)
        elif as_json:
            f.write(json.dumps(obj))
        else:
            f.write(obj if isinstance(obj, str) else pickle.dumps(obj))


def load_obj(fname, ftype='b', as_json=False):
    as_json = as_json or fname.lower().endswith('.json')
    if as_json:
        ftype = 't'

    with open(fname, 'r'+ftype) as f:
        if ftype == 'b':
            return pickle.load(f)
        elif as_json:
            return json.loads(f.read())
        else:
            return pickle.loads(f)


def listfiles(path, mask):
    for root, _, filenames in os.walk(path):
       for filename in fnmatch.filter(filenames, mask):
            yield os.path.join(root, filename)


def loadfile(filepath, mode='r'):
    with open(filepath, mode) as f:
        return f.read()


def savetext(fpath, content, enc='utf-8'):
    if isinstance(content, list):
        if content and content[0] and content[0][-1] not in ['\r', '\n']:
            savetext(fpath, '\n'.join(content), enc)
        else:
            savetext(fpath, ''.join(content), enc)
    else:
        with open(fpath, mode='wt', encoding=enc) as f:
            f.write(content)

    
def loadtxtf(fpath, enc='utf-8'):
    with open(fpath, mode='r', encoding=enc) as f:
        return f.read().split('\n')


def loadtext(fpath, enc='utf-8'):
    return loadtxtf(fpath, enc)

        
def loadfilefromzip(zip_file, filename='', fileindex=0):
    from zipfile import ZipFile
    with ZipFile(zip_file, mode='r') as zpf:
        filename = filename if filename else zpf.namelist()[fileindex]
        with zpf.open(filename) as f:
            return f.readlines()

        
def getfirstline(fpath, enc='utf-8'):
    with open(fpath, mode='r', encoding=enc) as f:
        txt = ''
        while True:
            data = f.read(2000)
            txt += data
            if len(data)<2000 or data.find('\n')>0:
                break
    return txt.split('\n')[0] 

    
def bigtxtiterator(filename, encoding='latin1', lend='\n'):
    from numpy import arange

    def process_lines(linhas):
        linhas = linhas.decode(encoding).split(lend)
        return linhas

    
    def fileend(fhandle):
        fhandle.seek(-1, 2)
        res = fhandle.tell()
        fhandle.seek(0, 0)
        return res
        
    def lastnewline(rwdata):
        sz = len(rwdata)
        for i in arange(sz, 0, -1):
            if rwdata[i-1] == 10:
                return (i-sz)+1
        return -sz
    
    chunksize = 1024*1024*50 #50MB
    f = open(filename, mode='rb')
    try:
        endpos = fileend(f)
        curpos = 0
        while curpos < endpos:
            raw = f.read(chunksize)
            curpos = f.tell()
            if raw:
                if curpos < endpos:
                    sk = lastnewline(raw)
                    raw = raw[0:sk-1]
                    f.seek(sk, 1)
                yield (curpos/endpos, process_lines(raw))
            else:
                break
    finally:
        f.close()


def save_session(session_name, __environment=globals().items()):
    import inspect as __inspXYZ
    import pyioutils.file_util as __fileutil
    ipython_vars = ['_ih', '_oh', '_dh', 'In', 'Out', 'get_ipython', 'exit', 'quit', '_']
    res = {'__imports': [], '__functions': {}}
    for k, v in __environment:
        if k in ipython_vars or k.startswith('_i') or k.split('_')[-1].isdigit() or k.startswith('__'):
            continue
        if v.__class__.__name__ == 'module':
            res['__imports'].append(f'import {k}' if k == v.__name__ else f'import {v.__name__} as {k}')
        elif v.__class__.__name__ == 'function':
            try:
                code = __inspXYZ.getsource(v)
            except OSError:
                print(f'Unable to get code for {k}')
                code = f'def {k}: raise OSError("could not get source code")'

            res['__functions'][k] = code

        elif not k.startswith('__'):
            res[k] = v
    __fileutil.dump_obj(session_name, list(res.items()))


class FileLockTimeout(Exception):
    pass


def wait_file_lock(lock_file, time_out=10, check_freq=0.1):
    has_time = int(time_out / check_freq)

    locked = path.isfile(lock_file)
    while locked and has_time:
        sleep(check_freq)
        locked = path.isfile(lock_file)
        has_time -= 1

    if locked:
        raise FileLockTimeout(f'Get file lock timeout "{lock_file}"')
    elif not open_exclusive(lock_file):
        wait_file_lock(lock_file, time_out=int(has_time*check_freq), check_freq=check_freq)


def open_exclusive(file_name, token=os.getpid):
    with open(file_name, 'a+') as fhandle:
        tkn = str(token() if callable(token) else token)
        n = fhandle.write(tkn)
        fhandle.seek(0, 0)
        return fhandle.read(n) == tkn

