"""Check and copy the frozen desk case; no network or model execution."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import zipfile
from xml.etree import ElementTree as ET
from research_skills.artifacts import validate_office
from research_skills.desk_audit import audit


def require(ok, message):
    if not ok:
        raise ValueError(message)


def compact(value):
    return re.sub(r'\s+', '', value)


def verify(root):
    def read(name):
        return json.loads((root/name).read_text(encoding='utf-8'))
    for name, digest in read('reviewed-inputs.json')['sha256'].items():
        target=(root/name).resolve()
        require(target.is_relative_to(root.resolve()), 'Path escapes case')
        require(hashlib.sha256(target.read_bytes()).hexdigest()==digest, 'Frozen file changed: '+name)
    sources={s['id']:s for s in read('sources.json')}
    claims={c['id']:c for c in read('claims.json')}
    pages=read('desk-research-content.json')
    require(len(sources)==len(read('sources.json')), 'Duplicate source IDs')
    require(len(claims)==len(read('claims.json')), 'Duplicate claim IDs')
    for c in claims.values():
        require(set(c['source_ids'])<=sources.keys(), 'Unknown claim source')
        for anchor in c.get('locators',[c.get('locator')]):
            require(anchor and anchor['anchor_end']>anchor['anchor_start'], 'Missing locator')
            require(len(anchor['anchor_sha256'])==64, 'Missing anchor digest')
    report=audit(read('research-map.json'))
    require(not report['findings'], 'Research structure has gaps')
    ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
    pptx=root/'deliverables/desk-research.pptx'
    with zipfile.ZipFile(pptx) as z:
        slide_parts=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
        require(len(slide_parts)==len(pages),'Slide count differs')
        tables=charts=0
        for p in pages:
            require(set(p['source_ids'])<=sources.keys(),'Unknown page source')
            require(set(p['claim_ids'])<=claims.keys(),'Unknown page claim')
            for cid in p['claim_ids']:
                require(set(claims[cid]['source_ids'])<=set(p['source_ids']),'Uncited claim')
            xml=ET.fromstring(z.read(f'ppt/slides/slide{p["number"]}.xml'))
            text=compact(''.join(xml.itertext()))
            expected=[p['title'],p['implication']]
            expected.extend(b if isinstance(b,str) else v for b in p['body'] for v in ([b] if isinstance(b,str) else b))
            for value in expected:
                require(compact(value) in text,'Narrative differs on '+p['id'])
            tables+=len(xml.findall('.//a:tbl',ns));charts+=len(xml.findall('.//c:chart',ns))
            if p['kind']=='chart':require(len(xml.findall('.//c:chart',ns))==1,'Missing native chart')
        require(charts==sum(p['kind']=='chart' for p in pages),'Native chart count differs')
        for name in z.namelist():
            if re.fullmatch(r'ppt/charts/chart\d+\.xml',name):
                xml=ET.fromstring(z.read(name))
                require(all(float(v.get('val'))==0 for v in xml.findall('.//c:valAx/c:scaling/c:min',ns)), 'Bar chart baseline is truncated')
                require(bool(xml.findall('.//c:valAx/c:scaling/c:min',ns)),'Bar chart minimum is not explicit')
        embedded=[n for n in z.namelist() if n.startswith('ppt/embeddings/') and n.endswith('.xlsx')]
        require(len(embedded)==charts,'Missing chart workbooks')
        with tempfile.TemporaryDirectory() as temp:
            for i,name in enumerate(embedded):
                target=Path(temp)/f'chart-{i}.xlsx';target.write_bytes(z.read(name));validate_office(target)
    result=validate_office(pptx)
    return {**report,**result,'native_charts':charts,'native_tables':tables,'embedded_workbooks':len(embedded),
            'replayed':['frozen_hashes','narrative_presence','citation_binding','research_structure','native_objects','zero_bar_baselines','microsoft_openxml'],
            'not_replayed':['live_retrieval','source_semantics','editorial_judgment','visual_judgment','fieldwork','external_skillopt']}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    root=Path(__file__).resolve().parent;result=verify(root)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    shutil.copy2(root/'deliverables/desk-research.pptx',out/'desk-research.pptx')
    shutil.copy2(root/'desk-research.zh-CN.md',out/'desk-research.zh-CN.md')
    (out/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False))
