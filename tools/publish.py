"""Trusted maintainer workflow. Never run this with secrets on a contributor branch."""
import argparse,base64,html,json,os,subprocess,tempfile,urllib.request
from pathlib import Path
import catalogue as c

def api(endpoint,payload=None,method=None):
    args=['gh','api',endpoint]
    if payload is None:
        if method:args+=['--method',method]
        return json.loads(subprocess.check_output(args,text=True) or '{}')
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',delete=False,suffix='.json') as f:
        json.dump(payload,f);name=f.name
    try:return json.loads(subprocess.check_output(args+['--method',method or 'POST','--input',name],text=True) or '{}')
    finally:Path(name).unlink(missing_ok=True)
def branch_file(name):
    try:return base64.b64decode(api(f'repos/{c.REPO}/contents/{name}?ref=catalogue')['content'])
    except subprocess.CalledProcessError:return None

def public_bytes(url,limit):
    with urllib.request.urlopen(url,timeout=60) as r:
        b=r.read(limit+1)
    assert len(b)<=limit,'Public download exceeds size limit'
    return b

def publish_branch(out):
    value=json.loads(json.loads((out/'catalogue.json').read_text(encoding='utf-8'))['payload'])
    cards=''.join('<article><h2>'+html.escape(p['manifest']['name'])+'</h2><p>'+html.escape(p['manifest']['description'])+'</p><a href="'+html.escape(p['url'],quote=True)+'">Download pack</a></article>' for p in value['packs'])
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>PaintFE community packs</title><style>body{font:17px system-ui;max-width:960px;margin:60px auto;padding:24px;background:#f6f5fa;color:#28263a}article{background:white;border:1px solid #dedbe5;border-radius:14px;padding:24px;margin:20px 0}a{color:#ad3900}</style><h1>PaintFE community packs</h1><p>Effects, themes and icon packs for PaintFE 1.5.0 or a compatible preview. PaintFE 1.4.28 does not include Community packs.</p><p><a href="https://github.com/'+c.REPO+'">Source, author guides and contributions</a></p>'+cards+'</html>'
    files={'catalogue.json':(out/'catalogue.json').read_text(encoding='utf-8'),'metrics.json':(out/'metrics.json').read_text(encoding='utf-8'),'.nojekyll':'','index.html':page}
    tree=api(f'repos/{c.REPO}/git/trees',{'tree':[{'path':name,'mode':'100644','type':'blob','content':content} for name,content in files.items()]})
    parent=None
    try:parent=api(f'repos/{c.REPO}/git/ref/heads/catalogue')['object']['sha']
    except subprocess.CalledProcessError:pass
    commit=api(f'repos/{c.REPO}/git/commits',{'message':'Refresh community catalogue and download statistics','tree':tree['sha'],'parents':[parent] if parent else []})
    if parent:api(f'repos/{c.REPO}/git/refs/heads/catalogue',{'sha':commit['sha'],'force':False},'PATCH')
    else:api(f'repos/{c.REPO}/git/refs',{'ref':'refs/heads/catalogue','sha':commit['sha']})
    try:api(f'repos/{c.REPO}/pages/builds',{},'POST')
    except subprocess.CalledProcessError:print('Pages is not configured yet; enable the catalogue branch as the Pages source.')

def reconcile(value,old):
    """Retain immutable URLs, first-publication dates and explicit source removals."""
    fresh=[]
    for i,p in enumerate(value['packs']):
        prior=old.get(p['manifest']['id'])
        if prior and prior['manifest']['version']==p['manifest']['version']:
            assert prior['sha256']==p['sha256'],'Changed plugin must have a new version'
            value['packs'][i]=prior
        else:
            if prior:p['published']=prior['published']
            fresh.append(p)
    assert fresh or set(old)!=set(p['manifest']['id'] for p in value['packs']),'No changed plugins. Use the statistics workflow to refresh the catalogue.'
    return fresh

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tag');parser.add_argument('--statistics',action='store_true');a=parser.parse_args()
    key=c.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(os.environ['PLUGIN_SIGNING_KEY']))
    assert key.public_key().public_bytes(c.Encoding.Raw,c.PublicFormat.Raw).hex()==(c.ROOT/'catalogue-public-key.hex').read_text().strip()
    out=c.ROOT/'dist';out.mkdir(exist_ok=True)
    previous=branch_file('catalogue.json');metrics=branch_file('metrics.json')
    if metrics:(out/'metrics.json').write_bytes(metrics)
    if a.statistics:
        assert previous,'Publish plugins before refreshing statistics';(out/'catalogue.json').write_bytes(previous)
    else:
        assert a.tag and c.re.fullmatch(r'v[0-9.]+',a.tag)
        value=c.build(a.tag,out,key);old={}
        if previous:old={p['manifest']['id']:p for p in json.loads(json.loads(previous)['payload'])['packs']}
        fresh=reconcile(value,old)
        try:release=api(f'repos/{c.REPO}/releases/tags/{a.tag}')
        except subprocess.CalledProcessError:
            release=api(f'repos/{c.REPO}/releases',{'tag_name':a.tag,'name':'Community packs '+a.tag,'body':'Community effects, themes and icon packs. Includes Two Tone, Paper Grain, Colour Offset, Soft Vignette, Glass Dark and Glass Light.\n\nRequires PaintFE 1.5.0 or a compatible preview. PaintFE 1.4.28 does not include Community packs. Installed effects run offline; themes and icons are applied only after preview. See the repository guides for installation and contribution instructions.','draft':False,'prerelease':True})
        existing={x['name']:x for x in release['assets']}
        for p in fresh:
            for url in [p['url'],p.get('icon_url',''),p.get('screenshot_url','')]:
                if not url:continue
                name=url.rsplit('/',1)[1];path=out/name
                if name in existing:assert c.sha(public_bytes(url,c.LIMIT))==c.sha(path.read_bytes()),'Published asset differs; do not replace it'
                else:subprocess.run(['gh','release','upload',a.tag,str(path),'--repo',c.REPO],check=True)
                assert c.sha(public_bytes(url,c.LIMIT))==c.sha(path.read_bytes()),'Public download verification failed'
        (out/'catalogue.json').write_bytes(c.envelope(value,key))
    c.refresh(out,key);publish_branch(out)
    print('Public assets verified; signed catalogue branch updated.')
if __name__=='__main__':main()
