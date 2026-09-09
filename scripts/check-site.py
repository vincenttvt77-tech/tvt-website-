#!/usr/bin/env python3
"""Check generated pages and their internal links without submitting forms."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re, subprocess, hashlib
root = Path(__file__).resolve().parent.parent
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.refs=[]; self.ids=[]; self.h1=0; self.main=0; self.forms=[]; self.feed(text)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.append(a['id'])
        if tag=='h1': self.h1+=1
        if tag=='main': self.main+=1
        if tag=='form': self.forms.append(a)
        for attr in ('href','src'):
            if a.get(attr): self.refs.append(a[attr])
        if a.get('style'): self.refs += re.findall(r'url\([\"\']?([^\)\"\']+)',a['style'])
errors=[]
manifest=json.loads((root/'src/pages.json').read_text())
pages={f.name:Page(f.read_text()) for f in root.glob('*.html') if f.name!='preview.html'}
for name, page in pages.items():
    if name!='creditmatch.html':
        if page.h1!=1: errors.append(f'{name}: expected one h1, found {page.h1}')
        if page.main!=1: errors.append(f'{name}: expected one main, found {page.main}')
    if len(page.ids)!=len(set(page.ids)): errors.append(f'{name}: duplicate ids')
    for ref in page.refs:
        u=urlsplit(ref)
        if u.scheme or u.netloc: continue
        target=unquote(u.path) or name
        if target.startswith('/'): target=target.lstrip('/')
        if not (root/target).exists(): errors.append(f'{name}: missing {target}')
        if u.fragment and target in pages and u.fragment not in pages[target].ids:
            errors.append(f'{name}: missing #{u.fragment} in {target}')
    for form in page.forms:
        if form.get('action')!='https://api.web3forms.com/submit': errors.append(f'{name}: unexpected form destination')
for match in re.findall(r'url\([\"\']?([^\)\"\']+)',(root/'tvt.css').read_text()):
    if not urlsplit(match).scheme and not (root/match).exists(): errors.append('CSS asset missing: '+match)
for slug in manifest:
    if not (root/'dist'/f'{slug}.html').exists(): errors.append('Not packaged: '+slug)
# The compiled app's executable code must remain exactly as supplied.
original=subprocess.check_output(['git','show','HEAD:creditmatch.html'],cwd=root,text=True)
current=(root/'creditmatch.html').read_text()
scripts=lambda text: re.findall(r'<script\b[^>]*>(.*?)</script>',text,re.S)
if scripts(original)!=scripts(current): errors.append('CreditMatch executable code changed')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} pages; local links, anchors, assets, form destinations, and landmarks checked.')
print('PASS: CreditMatch application code unchanged.')
print('Original logo SHA-256:',hashlib.sha256((root/'assets/tvt-logo.png').read_bytes()).hexdigest())
