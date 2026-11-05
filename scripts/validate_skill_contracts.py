#!/usr/bin/env python3
"""Read-only validation of the source skill graph; performs no provider action."""
import json
import re
from pathlib import Path

def validate(root: Path) -> list[str]:
    errors=[]
    registry=json.loads((root/'docs/WORKFLOW-CONTRACTS.json').read_text(encoding='utf-8'))
    for key in ('rules','fundamentals'):
        if not (root/registry[key]).is_file(): errors.append(f'missing {key}: {registry[key]}')
    skills={p.parent.name:p for p in (root/'skills').glob('*/SKILL.md')}
    for name,path in skills.items():
        text=path.read_text(encoding='utf-8')
        front=text.split('---',2)[1] if text.startswith('---\n') and len(text.split('---',2))==3 else ''
        if not re.search(r'^name: '+re.escape(name)+r'\s*$',front,re.M): errors.append(f'{name}: invalid name/frontmatter')
        if not re.search(r'^description: .+',front,re.M): errors.append(f'{name}: missing description')
    ids=[w['id'] for w in registry['workflows']]
    if len(ids)!=len(set(ids)): errors.append('duplicate workflow IDs')
    for w in registry['workflows']:
        for skill in [w['entry'],*w['specialists']]:
            if skill not in skills:errors.append(f'{w["id"]}: missing skill {skill}')
        if w['next'] is not None and w['next'] not in ids: errors.append(f'{w["id"]}: missing next workflow')
        if not w['outputs'] or not w['review_scope']:errors.append(f'{w["id"]}: missing handoff contract')
    return errors

if __name__=='__main__':
    import sys
    errors=validate(Path(__file__).resolve().parents[1])
    print('\n'.join(errors) if errors else 'Skill graph, references and handoff contracts valid')
    sys.exit(bool(errors))
