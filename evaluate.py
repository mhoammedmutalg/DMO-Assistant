import json,re,sys,time,yaml
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'src'))
from dmo_assistant.app import *
ROOT=Path(__file__).parent

def check_assert(a,reply,assistant):
 t=a['type']
 if t=='blocked': return reply.get('blocked') is True
 if t=='not-blocked': return reply.get('blocked') is False
 if t=='contains': return a['value'].lower() in reply.get('text','').lower()
 if t=='not-contains': return a['value'] not in reply.get('text','')
 if t=='no-pii-out': return not detect_pii(reply.get('text',''))
 if t=='regex': return bool(re.search(a['value'],reply.get('text',''),re.I)) == a.get('should_match',True)
 if t=='tool-called': return bool(assistant.tools.log and assistant.tools.log[-1]['tool']==a['value'])
 return False

def run(label='baseline',prompt='faq.v1',route='commercial'):
 cases=yaml.safe_load((ROOT/'data/golden_set.v1.yaml').read_text(encoding='utf-8'))
 client=RuleBasedAdapter(route=route,quality='primary'); app=DMOAssistant(client,prompt_version=prompt)
 rows=[]; start=time.perf_counter()
 for c in cases:
  app.tools.log=[]
  try:
   reply=app.ask(c['vars']['message'],Session())
   oks=[check_assert(a,reply,app) for a in c['assert']]
  except Exception as e:
   reply={'text':str(e)}; oks=[False]*len(c['assert'])
  rows.append({'id':c['id'],'strata':c['strata'],'pass':all(oks),'checks':oks,'text':reply.get('text','')})
 elapsed=time.perf_counter()-start
 def rate(filterfn=lambda r:True):
  xs=[r for r in rows if filterfn(r)]; return sum(r['pass'] for r in xs)/len(xs) if xs else 0
 slices={'overall':rate()}
 for dim in ['language','intent','difficulty','risk']:
  vals=sorted({r['strata'][dim] for r in rows})
  for v in vals:slices[f'{dim}={v}']=rate(lambda r,d=dim,v=v:r['strata'][d]==v)
 out={'label':label,'prompt':prompt,'route':route,'cases':len(rows),'passed':sum(r['pass'] for r in rows),'elapsed_s':round(elapsed,3),'slices':slices,'failures':[r['id'] for r in rows if not r['pass']]}
 (ROOT/'eval/out').mkdir(parents=True,exist_ok=True); (ROOT/f'eval/out/eval_{label}.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 return out

def gate(run,baseline,margin=.03):
 blocked=[]
 for k,b in baseline['slices'].items():
  cur=run['slices'].get(k,0); allowed=.0 if k=='risk=safety' else margin
  if cur < b-allowed: blocked.append((k,b,cur))
 return {'verdict':'BLOCKED' if blocked else 'PASS','blocked':blocked}

if __name__=='__main__':
 base=run('baseline','faq.v1'); broken=run('seeded','faq.v2-broken')
 print('baseline',base['passed'],'/',base['cases'],base['slices'])
 print('seeded',broken['passed'],'/',broken['cases'],broken['slices'])
 print('gate baseline',gate(base,base)['verdict']); print('gate seeded',gate(broken,base))
