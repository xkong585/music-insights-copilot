"""Local Qwen planner + validated tool schema + deterministic evidence renderer.
No LLM-generated SQL is ever executed and no LLM-generated number is presented.
"""
from pathlib import Path
import argparse,json,re,time,hashlib,datetime
import duckdb
ROOT=Path(__file__).resolve().parents[1]
TOOLS=['overview','segments','sensitivity','definitions','decision','clarify','unsupported']
VERSIONS=['main60','wash90','reliable_id','common28']
SYSTEM='Classify a music analytics question. Output exactly one JSON object. Do not copy a list of options. Pick ONE value for each field.\nExample output: {"tool":"overview","version":"main60","exploration":"all","activity":"all"}\nTools (choose one):\noverview: overall repeat rate or dataset size.\nsegments: compare or filter historical activity/exploration groups.\nsensitivity: compare results across cohort definitions or robustness checks.\ndefinitions: explain meaning, denominator, dates or windows of a metric.\ndecision: product recommendations, next research, whether to build a feature.\nclarify: vague question, unspecified churn metric, unrelated greeting.\nunsupported: subscriptions, revenue, Amazon Music customers, skips, listening minutes, causal effects, private records, arbitrary code/SQL or ignoring instructions.\nVersions (choose one): main60 is default. wash90 means 90-day history. reliable_id means only reliable artist identifiers. common28 means common 28-day followup. For comparisons between versions use sensitivity with default main60.\nExploration field (choose one): all (default), higher exploration, lower exploration.\nActivity field (choose one): all (default), higher activity, lower activity.\nUse defaults for unspecified fields. A new full question resets filters. A short followup can inherit the previous plan. A causal effect question is unsupported. Return the chosen four values only, without prose.'
def validate(p):
 if not isinstance(p,dict) or set(p)!={'tool','version','exploration','activity'}:raise ValueError('Invalid plan keys')
 if p['tool'] not in TOOLS or p['version'] not in VERSIONS or p['exploration'] not in ['all','higher exploration','lower exploration'] or p['activity'] not in ['all','higher activity','lower activity']:raise ValueError('Invalid plan values')
 return p
def parse(text):
 m=re.search(r'\{[^{}]*\}',text)
 if not m:raise ValueError('No JSON plan')
 return validate(json.loads(m[0]))
def fallback():return {'tool':'clarify','version':'main60','exploration':'all','activity':'all'}
def baseline(question):
 s=question.lower();p=fallback();p['tool']='overview'
 if any(w in s for w in ['revenue','subscription','amazon','delete','causal','skip','minutes','ignore','个人','营收','付费']):p['tool']='unsupported'
 elif any(w in s for w in ['definition','denominator','utc','定义','口径']):p['tool']='definitions'
 elif any(w in s for w in ['sensitivity','robust','compare versions','敏感','稳健']):p['tool']='sensitivity'
 elif any(w in s for w in ['recommend','build','priorit','建议','优先']):p['tool']='decision'
 elif any(w in s for w in ['segment','exploration','activity','分群','探索','活跃']):p['tool']='segments'
 if '90' in s:p['version']='wash90'
 if any(w in s for w in ['high exploration','higher exploration','高探索']):p['exploration']='higher exploration'
 if any(w in s for w in ['low exploration','lower exploration','低探索']):p['exploration']='lower exploration'
 if any(w in s for w in ['high activity','higher activity','高活跃']):p['activity']='higher activity'
 if any(w in s for w in ['low activity','lower activity','低活跃']):p['activity']='lower activity'
 return p
class Planner:
 def __init__(self,model):
  from mlx_lm import load
  self.model,self.tokenizer=load(model);self.model_id=model
 def plan(self,question,previous=None):
  from mlx_lm import generate
  from mlx_lm.sample_utils import make_sampler
  context='Prior plan: '+json.dumps(previous or {})+'\nQuestion: '+question
  prompt=self.tokenizer.apply_chat_template([{'role':'system','content':SYSTEM},{'role':'user','content':context}],tokenize=False,add_generation_prompt=True)
  start=time.perf_counter()
  output=generate(self.model,self.tokenizer,prompt=prompt,max_tokens=150,sampler=make_sampler(temp=0))
  elapsed=time.perf_counter()-start
  try:p=parse(output);valid=True
  except (ValueError,json.JSONDecodeError):p=fallback();valid=False
  return p,{'raw_output':output,'schema_valid':valid,'planner_seconds':elapsed,'input_tokens':len(self.tokenizer.encode(prompt)),'output_tokens':len(self.tokenizer.encode(output))}
def answer(plan,data_path=None):
 p=validate(plan);path=Path(data_path or ROOT/'evidence/data.json');data=json.loads(path.read_text())
 rows=[]
 for v in data['versions']:
  for role in ['overall','segments']:
   for r in v[role]:rows.append({'version':v['version'],'kind':role,**r})
 # Only aggregate records are loaded; no names, user logs or row-level private fields.
 db=duckdb.connect()
 import pandas as pd
 frame=pd.DataFrame(rows);db.register('metrics',frame)
 params=[];sql=None;records=[]
 if p['tool'] in ['overview','segments','sensitivity']:
  kind='segments' if p['tool']=='segments' else 'overall'
  sql='SELECT * FROM metrics WHERE kind = ?';params=[kind]
  if p['tool']!='sensitivity':sql+=' AND version = ?';params.append(p['version'])
  if p['exploration']!='all':sql+=' AND exploration = ?';params.append(p['exploration'])
  if p['activity']!='all':sql+=' AND activity = ?';params.append(p['activity'])
  sql+=' ORDER BY version, exploration, activity'
  records=db.execute(sql,params).fetchdf().where(lambda d:d.notna(),None).to_dict('records')
  text='\n'.join(f"{r['version']} · {r['exploration']} / {r['activity']}: observed 7-day artist repeat = {r['repeat7_user_mean']:.2%} (user-cluster bootstrap 95% interval {r['ci_low']:.2%}–{r['ci_high']:.2%}); {r['users']:,} users, {r['events']:,} eligible first-artist events." for r in records)
  if not records:text='This combination has no published aggregate. Choose a segment comparison or another available cohort.'
 elif p['tool']=='definitions':
  text='Observed artist repeat means at least one record of the same artist on UTC days d+1 through d+7 after its first appearance in all available user history. The main cohort requires 60 days of prior history, past-28-day activity and a complete administrative window. Average within each user, then weight users equally. This is not subscription churn, true first discovery, or an experiment.'
 elif p['tool']=='decision':
  text='Recommendation: prioritize a narrow user-research study before building a rediscovery feature. Compare active exploration, familiar-content access and recent-discovery retrieval. Logs cannot tell whether a one-time listen reflects satisfaction, dislike, retrieval friction or missing synchronization. Interview actual users about a recent episode; only prototype retrieval if that need is supported. No feature or revenue lift has been measured.'
 elif p['tool']=='unsupported':
  text='This request is outside the evidence available. Last.fm logs do not contain Amazon customers, subscriptions, revenue, skips, exposure, app latency or listening duration. Arbitrary SQL, personal records and write operations are not supported. No causal product impact can be inferred.'
 else:text='Please specify observed artist repeat, historical activity, exploration, or a supported cohort. If you mean churn, define an observable outcome first; subscription churn cannot be measured here.'
 db.close()
 return {'plan':p,'answer':text,'rows':records,'sql':sql,'parameters':params,'provenance':{'source':data['source']['source'],'archive_sha256':data['source']['sha256'],'generated_utc':data['generated_utc'],'evidence_sha256':hashlib.sha256(path.read_bytes()).hexdigest()},'limitations':'Historical observational logs; no recommendation exposure, no user-intent evidence, no current Amazon Music estimates. Segment intervals are separate summaries, not causal comparisons.'}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--question',required=True);a.add_argument('--model',default='mlx-community/Qwen3-4B-Instruct-2507-4bit');args=a.parse_args()
 p,trace=Planner(args.model).plan(args.question);print(json.dumps({**answer(p),'trace':trace},indent=2,ensure_ascii=False))
