# -*- coding: utf-8 -*-
"""Враг -> шрифт его реплик. Chatter.TextPrefab (raw) -> TMP -> m_fontAsset
(скан байтов на PPtr, указывающий на известный TMP_FontAsset)."""
import os, re, struct, UnityPy
ROOT=r'C:\Users\User\Downloads\gunsaw-demo-win'; DATA=os.path.join(ROOT,'Gunsaw_Data')
CATS=['alert','spot','reload','allyDeath','death','ouch']
files=['globalgamemanagers.assets','resources.assets']
files+=sorted([f for f in os.listdir(DATA) if re.match(r'^level\d+$',f)])
files+=sorted([f for f in os.listdir(DATA) if re.match(r'^sharedassets\d+\.assets$',f)])
files=[f for f in files if os.path.exists(os.path.join(DATA,f))]
envs={}; index={}
for f in files:
    e=UnityPy.load(os.path.join(DATA,f)); envs[f]=e; index[f]={o.path_id:o for o in e.objects}

# все TMP_FontAsset: (basename, pathid)->name
fonts={}
for f in files:
    for o in envs[f].objects:
        if o.type.name!='MonoBehaviour': continue
        try:
            mb=o.read(check_read=False); ms=mb.m_Script.read()
            if ms.m_ClassName=='TMP_FontAsset': fonts[(os.path.basename(f).lower(),o.path_id)]=mb.m_Name
        except Exception: continue

def a4(i): return (i+3)&~3
def rstr(b,i):
    ln=struct.unpack_from('<i',b,i)[0]
    if ln<0 or i+4+ln>len(b): raise ValueError('bad')
    return b[i+4:i+4+ln].decode('utf-8','replace'),a4(i+4+ln)
def textprefab_pptr(b):
    i=12+4+12; _,i=rstr(b,i)
    for _ in CATS:
        n=struct.unpack_from('<i',b,i)[0]; i+=4
        for _ in range(n): _,i=rstr(b,i)
    i=a4(i)+4
    return struct.unpack_from('<i',b,i)[0], struct.unpack_from('<q',b,i+4)[0]
def resolve(srcfile,srcobj,fid,pid):
    if pid==0: return None
    if fid==0:
        if pid in index[srcfile]: return (srcfile,index[srcfile][pid])
    else:
        try: exts=[os.path.basename(x.path).lower() for x in srcobj.assets_file.externals]
        except Exception: exts=[]
        if 1<=fid<=len(exts):
            tgt=exts[fid-1]
            for f in files:
                if os.path.basename(f).lower()==tgt and pid in index[f]: return (f,index[f][pid])
    for f in files:
        if pid in index[f]: return (f,index[f][pid])
    return None
def font_of_textprefab(srcfile,pobj):
    go=pobj.read()
    comps=getattr(go,'m_Components',None)
    if not comps: return '(no comps)'
    for c in comps:
        pid=getattr(c,'path_id',0); objr=index[srcfile].get(pid)
        if objr is None or objr.type.name!='MonoBehaviour': continue
        raw=objr.get_raw_data()
        if len(raw)<300: continue   # TMP крупный
        try: exts=[os.path.basename(x.path).lower() for x in objr.assets_file.externals]
        except Exception: exts=[]
        def filefor(fid): return srcfile if fid==0 else (exts[fid-1] if 1<=fid<=len(exts) else None)
        for off in range(0,len(raw)-12):
            fid=struct.unpack_from('<i',raw,off)[0]
            if fid<0 or fid>6: continue
            fp=struct.unpack_from('<q',raw,off+4)[0]
            tf=filefor(fid)
            if tf and (tf,fp) in fonts: return fonts[(tf,fp)]
    return '(font?)'
def go_tr(go):
    for c in getattr(go,'m_Components',[]) or []:
        try:
            r=c.read()
            if r.object_reader.type.name in ('Transform','RectTransform'): return r
        except Exception: pass
    return None
def root_name(go):
    n=getattr(go,'m_Name','(?)'); tr=go_tr(go); s=0
    while tr is not None and s<64:
        s+=1; f=getattr(tr,'m_Father',None)
        if f is None or getattr(f,'path_id',0)==0: break
        try: tr=f.read(); n=tr.m_GameObject.read().m_Name
        except Exception: break
    return n

seen={}
for f in files:
    for obj in envs[f].objects:
        if obj.type.name!='MonoBehaviour': continue
        try:
            mb=obj.read(check_read=False)
            if mb.m_Script.read().m_ClassName!='Chatter': continue
            base=re.sub(r' \(\d+\)$','',root_name(mb.m_GameObject.read()))
            fid,pid=textprefab_pptr(obj.get_raw_data())
            r=resolve(f,obj,fid,pid)
            font='(no prefab)' if r is None else font_of_textprefab(r[0],r[1])
            seen.setdefault(base,{}).setdefault(font,0)
            seen[base][font]+=1
        except Exception: continue

print("=== враг -> шрифт реплик ===")
for k in sorted(seen):
    parts=', '.join('%s'%fn for fn in sorted(seen[k]))
    print("  %-20s %s"%(k,parts))
