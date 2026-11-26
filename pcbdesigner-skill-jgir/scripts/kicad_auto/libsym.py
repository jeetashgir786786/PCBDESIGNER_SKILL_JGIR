import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from sexp import parse,find
import kenv
LIBDIR=kenv.sym_dir()
_cache={}
def load_lib(lib):
    if lib not in _cache:
        _cache[lib]=parse(open(f'{LIBDIR}/{lib}.kicad_sym').read())[0]
    return _cache[lib]
def get_symbol(lib,name):
    L=load_lib(lib)
    for s in find(L,'symbol'):
        if s[1].strip('"')==name: 
            # resolve extends
            ext=find(s,'extends')
            if ext:
                base=get_symbol(lib,ext[0][1].strip('"'))
                import copy
                b=copy.deepcopy(base)
                b[1]='"'+name+'"'
                # replace properties with derived ones
                props={p[1]:p for p in find(s,'property')}
                for i,it in enumerate(b):
                    if isinstance(it,list) and it and it[0]=='property' and it[1] in props:
                        b[i]=props[it[1]]
                # rename sub-units
                bn=ext[0][1].strip('"')
                for it in b:
                    if isinstance(it,list) and it and it[0]=='symbol':
                        it[1]=it[1].replace(bn,name,1)
                return b
            return s
    raise KeyError(name)
def pins(sym):
    out=[]
    def walk(x,unit):
        for it in x:
            if isinstance(it,list) and it:
                if it[0]=='symbol':
                    nm=it[1].strip('"'); u=int(nm.split('_')[-2]) if nm.count('_')>=2 else 0
                    walk(it,u)
                elif it[0]=='pin':
                    at=find(it,'at')[0]; ln=float(find(it,'length')[0][1])
                    name=find(it,'name')[0][1].strip('"'); num=find(it,'number')[0][1].strip('"')
                    out.append(dict(num=num,name=name,type=it[1],x=float(at[1]),y=float(at[2]),ang=float(at[3]) if len(at)>3 else 0,len=ln,unit=unit))
    walk(sym,0)
    return out
if __name__=='__main__':
    lib,name=sys.argv[1].split(':')
    s=get_symbol(lib,name)
    for p in pins(s): print(p['num'],p['name'],p['type'],p['unit'])
    for p in find(s,'property'): print(p[1],p[2])
