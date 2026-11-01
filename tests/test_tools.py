from pathlib import Path
import sys,json,pytest
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'))
from copilot import validate,parse,answer,fallback
def test_reject_arbitrary_tool():
 p=fallback();p['tool']='execute_sql'
 with pytest.raises(ValueError):validate(p)
def test_reject_extra_sql_payload():
 with pytest.raises(ValueError):validate({**fallback(),'sql':'DROP TABLE metrics'})
def test_reject_sql_in_filter():
 p=fallback();p['activity']="all';DROP TABLE metrics;--"
 with pytest.raises(ValueError):validate(p)
def test_reject_non_json():
 with pytest.raises(ValueError):parse('Here is made up SQL.')
def test_overview_trace_has_actual_evidence_hash():
 p=fallback();p['tool']='overview';r=answer(p);assert r['rows'] and len(r['provenance']['evidence_sha256'])==64;assert r['parameters']==['overall','main60']
def test_group_filter_matches():
 p=fallback();p.update(tool='segments',exploration='higher exploration',activity='lower activity');r=answer(p);assert len(r['rows'])==1;assert r['rows'][0]['exploration']=='higher exploration'
def test_sensitivity_contains_four_versions():
 p=fallback();p['tool']='sensitivity';assert len(answer(p)['rows'])==4
def test_unsupported_produces_no_sql():
 p=fallback();p['tool']='unsupported';r=answer(p);assert r['sql'] is None and not r['rows'];assert 'outside' in r['answer']
def test_definitions_do_not_claim_causal_effect():
 p=fallback();p['tool']='definitions';r=answer(p);assert 'not subscription churn' in r['answer']
def test_benchmark_failure_records_preserved():
 e=json.loads((R/'evidence/evaluation.json').read_text());runs=json.loads((R/'evidence/runs.json').read_text());assert len(runs)==e['cases'];assert sum(not r['exact'] for r in runs)==len(e['errors'])
