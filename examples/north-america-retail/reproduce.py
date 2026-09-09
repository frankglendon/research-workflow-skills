"""Recompile a reviewed case and replay its recorded handoff, with zero model calls."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from research_skills import study, survey_design, survey_export
from research_skills.artifacts import validate_office
from research_skills.contracts import GateError


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    source=Path(__file__).resolve().parent; output=Path(args.output).resolve()
    manifest=json.loads((source/'reviewed-inputs.json').read_text(encoding="utf-8"))
    for name,expected in manifest['sha256'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise GateError('Reviewed input paths must stay within the case')
        if hashlib.sha256((source/name).read_bytes()).hexdigest()!=expected:
            raise GateError('Case changed; perform a new content review before replay')
    output.mkdir(parents=True,exist_ok=False)
    for name in ['research-plan.md','qualitative-guide.md','programming-guide.md','analysis-plan.md','questionnaire-spec.json','codebook-plan.json','study-plan.json']:
        shutil.copyfile(source/name,output/name)
    shutil.copyfile(source/'deliverables/research-plan.docx',output/'research-plan.docx')
    validate_office(output/'research-plan.docx')
    spec=json.loads((output/'questionnaire-spec.json').read_text(encoding="utf-8"))
    codebook=json.loads((output/'codebook-plan.json').read_text(encoding="utf-8"))
    survey_export.questionnaire(spec,output/'questionnaire.xlsx')
    survey_export.codebook(spec,codebook,output/'codebook.xlsx')
    study.initialize(output,json.loads((output/'study-plan.json').read_text(encoding="utf-8")))
    artifacts={'design':[('plan','research-plan.docx'),('qualitative','qualitative-guide.md'),('analysis','analysis-plan.md')],
               'questionnaire':[('questionnaire','questionnaire.xlsx'),('programming','programming-guide.md')],
               'codebook':[('codebook','codebook.xlsx')]}
    reviews=json.loads((source/'case-review.json').read_text(encoding="utf-8"))
    for sid in artifacts:
        study.start(output,sid,'recorded-case-replay',study.status(output)['revision'])
        current=study.submit(output,sid,[{'id':k,'path':v} for k,v in artifacts[sid]],study.status(output)['revision'])
        candidate=next(s for s in current['stages'] if s['id']==sid)['candidate_sha256']
        study.review(output,sid,{'candidate_sha256':candidate,'execution_id':'recorded-case-replay',
                                'criteria':reviews[sid]},current['revision'])
        study.complete(output,sid,study.status(output)['revision'])
    result=study.manifest(output)
    result.update(model_calls=0,review_mode='recorded_host_review_replay',fieldwork_executed=False,
                  office_outputs=3,openxml_errors=0,**survey_design.check_paths(spec))
    (output/'stage-manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'complete':result['complete'],'office_outputs':3,'openxml_errors':0,
                      'model_calls':0,**survey_design.check_paths(spec)}))


if __name__=='__main__': main()
