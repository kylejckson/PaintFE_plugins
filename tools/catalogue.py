"""Deterministic packages and download statistics. Scripts are never executed here."""
import argparse, base64, copy, hashlib, io, json, math, os, re, struct, subprocess, time, zipfile
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
REPO='kylejckson/PaintFE_plugins'
ROOT=Path(__file__).resolve().parents[1]
LIMIT=16*1024*1024
ID=re.compile(r'[a-z][a-z0-9_.-]{0,79}\Z')
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def portable(s):
    stem=s.split('.')[0].upper()
    return bool(s) and not s.endswith('.') and stem not in {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(1,10)],*[f'LPT{i}' for i in range(1,10)]}
def resource(s):return isinstance(s,str) and len(s)<=160 and all(re.fullmatch(r'[A-Za-z0-9_.-]+',p) and portable(p) and p not in ('.','..') for p in s.split('/'))
def unique(pairs):
    out={}
    for k,v in pairs:assert k not in out,'Duplicate JSON key';out[k]=v
    return out

def check_parameter(p):
    assert set(p)<=set('id label kind default help group min max step choices'.split()),'Unknown parameter field'
    assert ID.fullmatch(p['id']) and not any(c in p['id'] for c in '.-'),'Invalid parameter id'
    assert 0<len(p['label'])<=80 and len(p.get('help',''))<=1000
    assert isinstance(p.get('group',''),str) and len(p.get('group',''))<=80,'Invalid parameter group'
    kind=p['kind'];v=p['default']
    lo,hi,step=p.get('min',0),p.get('max',1),p.get('step',1)
    assert all(isinstance(n,(int,float)) and math.isfinite(n) for n in (lo,hi,step)) and lo<=hi and step>0
    if kind=='integer':assert all(n==int(n) for n in (lo,hi,step)) and step>=1 and -(2**63)<=lo and hi<2**63,'Invalid integer bounds'
    if kind in ('number','integer'):assert type(v) in (int,float) and math.isfinite(v) and lo<=v<=hi and (kind!='integer' or v==int(v))
    elif kind=='boolean':assert type(v) is bool
    elif kind=='text':assert isinstance(v,str) and len(v)<=2048
    elif kind=='colour':assert isinstance(v,list) and len(v)==4 and all(type(c) is int and 0<=c<=255 for c in v)
    elif kind=='choice':assert 0<len(p['choices'])<=64 and v in p['choices'] and all(isinstance(c,str) and 0<len(c)<=80 for c in p['choices'])
    else:raise AssertionError('Unknown parameter kind')
def source_manifest(directory):
    assert (directory/'manifest.json').stat().st_size<=512*1024
    m=json.loads((directory/'manifest.json').read_text(encoding='utf-8'),object_pairs_hook=unique);assert m['schema']==m['api']==1
    assert set(m)<=set('schema api id version name author description license tags effects files icon menu_light menu_dark screenshot'.split()),'Unknown manifest field'
    assert ID.fullmatch(m['id']) and re.fullmatch(r'\d{1,8}\.\d{1,8}\.\d{1,8}',m['version'])
    for key,maximum in [('name',80),('author',80),('description',4096),('license',120)]:assert isinstance(m[key],str) and 0<len(m[key])<=maximum and not any(ord(c)<32 and not (key=='description' and c in '\n\t') for c in m[key])
    assert 0<len(m['effects'])<=16 and len(m['tags'])<=12 and all(isinstance(t,str) and 0<len(t)<=40 for t in m['tags'])
    assert all(portable(part) for part in m['id'].split('.'))
    ids=set();files={}
    for e in m['effects']:
        assert set(e)<=set('id name category script description parameters histogram'.split()),'Unknown effect field'
        assert ID.fullmatch(e['id']) and e['id'] not in ids;ids.add(e['id'])
        assert 0<len(e['name'])<=80 and 0<len(e['category'])<=40
        assert resource(e['script']) and e['script'].endswith('.rhai')
        assert len(e.get('parameters',[]))<=24
        seen=set()
        for p in e.get('parameters',[]):check_parameter(p);assert p['id'] not in seen;seen.add(p['id'])
        b=(directory/e['script']).read_bytes();assert len(b)<=256*1024;b.decode('utf-8')
    for path in sorted(directory.rglob('*')):
        assert not path.is_symlink(),'Links are not allowed'
        if path.is_dir() or path.name=='manifest.json':continue
        name=path.relative_to(directory).as_posix();assert resource(name)
        assert name.endswith(('.rhai','.png','.md','.txt')) or name=='LICENSE'
        b=path.read_bytes();assert 0<len(b)<=4*1024*1024
        if name.endswith('.png'):
            assert b[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',b[16:24]);assert 0<w<=1600 and 0<h<=1200
        files[name]=b
    assert len(files)<=64 and sum(map(len,files.values()))<=LIMIT and 'LICENSE' in files
    for e in m['effects']:assert e['script'] in files
    for key in ('icon','menu_light','menu_dark','screenshot'):
        if m.get(key):assert m[key] in files and m[key].endswith('.png')
    m['files']=[{'path':name,'size':len(b),'sha256':sha(b)} for name,b in files.items()]
    return m,files

def envelope(value,key):
    payload=canonical(value)
    return canonical({'payload':payload.decode(),'signature':key.sign(payload).hex()})
def package(m,files,key):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,b in [('manifest.json',envelope(m,key)),*sorted(files.items())]:
            info=zipfile.ZipInfo(name,(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,b)
    b=out.getvalue();assert len(b)<=LIMIT;return b

def sources():return sorted((ROOT/'plugins').glob('*/*/manifest.json'))
def build(tag,out,key):
    out.mkdir(parents=True,exist_ok=True);entries=[];ids=set();now=int(time.time())
    for path in sources():
        m,files=source_manifest(path.parent);assert m['id'] not in ids;ids.add(m['id'])
        name=f"{m['id']}-{m['version']}.pfeplugin";b=package(m,files,key);(out/name).write_bytes(b)
        base=f'https://github.com/{REPO}/releases/download/{tag}/'
        artwork={}
        for field in ('icon','screenshot'):
            if m.get(field):
                artname=f"{m['id']}-{m['version']}-{field}.png";(out/artname).write_bytes(files[m[field]]);artwork[field+'_url']=base+artname
        entries.append({'manifest':m,'url':base+name,'sha256':sha(b),'size':len(b),'published':now,'updated':now,'downloads':0,'recent_downloads':0,'window_days':0,**artwork})
    value={'schema':1,'sequence':now,'updated':now,'packs':entries}
    (out/'catalogue.json').write_bytes(envelope(value,key));return value

def update_metrics(state,assets,now):
    """Stable asset IDs, bounded samples; counters never turn missing assets into negative downloads."""
    state=copy.deepcopy(state);records=state.setdefault('assets',{})
    for a in assets:
        ident=str(a['id']);count=int(a['download_count']);assert count>=0
        r=records.setdefault(ident,{'pack':a['pack'],'created':a['created'],'samples':[],'last':0,'offset':0})
        if count<r['last']:r['offset']+=r['last']
        r['last']=count;samples=r['samples'];samples.append([now,r['offset']+count])
        cutoff=now-8*86400
        while len(samples)>2 and samples[1][0]<cutoff:samples.pop(0)
    result={}
    for r in records.values():
        samples=r['samples'];total=r['offset']+r['last'];cut=now-7*86400
        before=[s for s in samples if s[0]<=cut]
        baseline=before[-1][1] if before else (0 if r['created']>=cut else samples[0][1])
        start=cut if before or r['created']>=cut else samples[0][0]
        # Do not count old or unavailable assets as currently trending.
        recent=max(0,total-baseline) if samples[-1][0]>cut else 0
        p=result.setdefault(r['pack'],{'downloads':0,'recent_downloads':0,'window_days':0})
        p['downloads']+=total;p['recent_downloads']+=recent;p['window_days']=max(p['window_days'],min(7,max(0,math.ceil((now-max(start,r['created']))/86400))))
    state['updated']=now;return state,result

def gh(*args):return subprocess.check_output(['gh',*args],text=True)
def refresh(out,key):
    c=json.loads(json.loads((out/'catalogue.json').read_text(encoding='utf-8'))['payload']);now=int(time.time())
    try:state=json.loads((out/'metrics.json').read_text(encoding='utf-8'))
    except FileNotFoundError:state={}
    pages=json.loads(gh('api',f'repos/{REPO}/releases?per_page=100','--paginate','--slurp'));assets=[]
    for page in pages:
        for release in page:
            for a in release['assets']:
                for p in c['packs']:
                    if re.fullmatch(re.escape(p['manifest']['id'])+r'-[0-9]+\.[0-9]+\.[0-9]+\.pfeplugin',a['name']):
                        from datetime import datetime
                        assets.append({**a,'pack':p['manifest']['id'],'created':int(datetime.fromisoformat(a['created_at'].replace('Z','+00:00')).timestamp())})
    state,counts=update_metrics(state,assets,now)
    for p in c['packs']:p.update(counts.get(p['manifest']['id'],{'downloads':0,'recent_downloads':0,'window_days':0}))
    c['updated']=now;c['sequence']=max(now,c['sequence']+1)
    (out/'metrics.json').write_bytes(canonical(state));(out/'catalogue.json').write_bytes(envelope(c,key))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['validate','build','refresh']);parser.add_argument('--tag');parser.add_argument('--out',default='dist');a=parser.parse_args()
    if a.command=='validate':
        ids=set()
        for path in sources():m,_=source_manifest(path.parent);assert m['id'] not in ids;ids.add(m['id']);print('Validated '+m['id'])
        return
    raw=os.environ.get('PLUGIN_SIGNING_KEY','');assert raw,'PLUGIN_SIGNING_KEY is required'
    key=Ed25519PrivateKey.from_private_bytes(bytes.fromhex(raw))
    assert key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex()==(ROOT/'catalogue-public-key.hex').read_text().strip(),'Signing key does not match catalogue-public-key.hex'
    if a.command=='build':assert a.tag and re.fullmatch(r'v[0-9.]+',a.tag);build(a.tag,Path(a.out),key)
    else:refresh(Path(a.out),key)
if __name__=='__main__':main()
