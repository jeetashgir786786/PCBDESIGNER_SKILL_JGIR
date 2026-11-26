import re
def parse(s):
    tok=re.compile(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+')
    stack=[[]]
    for m in tok.finditer(s):
        t=m.group(0)
        if t=='(':
            stack.append([])
        elif t==')':
            x=stack.pop(); stack[-1].append(x)
        else:
            stack[-1].append(t)
    return stack[0]
def dump(x,ind=0):
    if isinstance(x,list):
        if all(not isinstance(i,list) for i in x):
            return '('+' '.join(x)+')'
        parts=[]  # keep child order
        for i in x:
            parts.append(dump(i,ind+1) if isinstance(i,list) else i)
        return '('+' '.join(parts)+')'
    return x
def find(x,key):
    return [i for i in x if isinstance(i,list) and i and i[0]==key]
