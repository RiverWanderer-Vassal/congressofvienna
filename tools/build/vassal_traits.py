"""Codec for VASSAL piece and prototype definitions (+/id/TYPE/STATE), ported from VASSAL 3.7's
SequenceEncoder. decode_def/encode_def round-trip every definition in dist/buildFile.xml exactly."""
import html, re

def seq_decode(val, delim):
    toks=[]; start=0; n=len(val)
    if val is None: return toks
    i=0
    while True:
        buf=[]; i=start; tok=None
        while i<n:
            if val[i]==delim:
                if i>0 and val[i-1]=='\\':
                    buf.append(val[start:i-1]); start=i
                else:
                    buf.append(val[start:i]); start=i+1; break
            i+=1
        else:
            buf.append(val[start:n]); start=n+1
        t=''.join(buf)
        if len(t)>1 and t[0]=="'" and t[-1]=="'": t=t[1:-1]
        toks.append(t)
        if start>n: break
    return toks

def _esc(s, delim):
    return s.replace(delim, '\\'+delim)

def seq_encode(items, delim):
    out=[]
    for s in items:
        if s is None or s=='': out.append(''); continue
        if s[0]=='\\' or (s[0]=="'" and s[-1]=="'"):
            out.append("'"+_esc(s,delim)+"'")
        else: out.append(_esc(s,delim))
    return delim.join(out)

def split_chain(s):
    """type or state chain -> list of per-trait strings (outer first)."""
    res=[]
    while True:
        t=seq_decode(s,'\t')
        res.append(t[0])
        if len(t)<2: break
        s=t[1]
        if len(t)>2: raise ValueError('unexpected tokens')
    return res

def join_chain(parts):
    # build from inside out using raw (unescaped) inner strings
    inner=None
    for p in reversed(parts):
        if inner is None:
            inner=p
        else:
            inner=seq_encode([p,inner],'\t')
    return inner

def decode_def(text):
    """text: XML-unescaped element text '+/null/TYPE/STATE'"""
    t=seq_decode(text,'/')
    assert t[0]=='+', t[:2]
    pid=t[1]; typ=t[2]; state=t[3] if len(t)>3 else ''
    return pid, split_chain(typ), split_chain(state) if state else []

def encode_def(pid, types, states):
    return seq_encode(['+',pid,join_chain(types),join_chain(states)],'/')

def nks(code,name): return f"{code},0,{name}"
def dp_cmd(key, changer_type, value, menu=''):
    changer=seq_encode([changer_type, value], ',')
    return seq_encode([menu, key, changer], ':')
def dp_type(name, cmds, desc, numeric='false', mn='0', mx='100', wrap='false'):
    return seq_encode(['PROP', name, seq_encode([numeric,mn,mx,wrap],','), seq_encode(cmds, ','), desc], ';')
def calc_type(name, expr, desc):
    return seq_encode(['calcProp', name, expr, desc], ';')
