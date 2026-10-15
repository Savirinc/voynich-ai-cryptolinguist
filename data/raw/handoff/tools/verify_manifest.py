from pathlib import Path
import hashlib, json, sys
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'MANIFEST.json').read_text())
errors=[]
for item in manifest['files']:
    p=root/item['path']
    if not p.is_file(): errors.append('MISSING '+str(p)); continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h != item['sha256']: errors.append('HASH MISMATCH '+str(p))
print('Verified',len(manifest['files'])-len(errors),'of',len(manifest['files']),'files')
for e in errors: print(e)
sys.exit(bool(errors))
