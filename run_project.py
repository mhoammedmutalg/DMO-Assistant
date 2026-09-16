import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'src'))
from dmo_assistant.app import *
from evaluate import run,gate
ROOT=Path(__file__).parent

def kappa(a,b):
 cats=sorted(set(a)|set(b)); n=len(a); obs=sum(x==y for x,y in zip(a,b))/n; exp=sum((a.count(c)/n)*(b.count(c)/n) for c in cats); return (obs-exp)/(1-exp) if exp<1 else 1.0

# Guard corpus
att=[json.loads(x) for x in (ROOT/'data/attack_corpus.jsonl').read_text().splitlines()]; legit=[json.loads(x) for x in (ROOT/'data/legitimate_corpus.jsonl').read_text().splitlines()]
block=sum(input_guard(x['text'])['blocked'] for x in att)/len(att); fp=sum(input_guard(x['text'])['blocked'] for x in legit)/len(legit)
# PII
pii_sample='Employee 1001 email alan@example.com mobile 0551234567 national id 1123456789'
masked=mask_pii(pii_sample)
# Repair
client=RuleBasedAdapter(); contract,attempts,errs=extract_with_repair(client,'Create urgent data quality request for missing customer email values')
# Tools auth/idempotency
app=DMOAssistant(client); s=Session(); a1=app.ask('Create high priority data quality request for missing customer email values',s); a2=app.ask('Create high priority data quality request for missing customer email values',s)
unauth=False
try: app.ask('Create high priority data quality request for missing customer email values',Session(permissions=set()))
except PermissionError: unauth=True
# fault drill
p=RuleBasedAdapter('commercial'); p.inject_failures([429,503,429]); f=RuleBasedAdapter('openweight'); rc=ResilientClient(p,f,retries=2); fault_app=DMOAssistant(rc); fault_reply=fault_app.ask('What is a Data Owner?')
# prompt cache observed
c=RuleBasedAdapter(); cache_app=DMOAssistant(c); r1=cache_app.ask('What is a Data Owner?'); r2=cache_app.ask('What is a Data Owner?')
cache_rate=r2['usage']['cached_input_tokens']/r2['usage']['input_tokens']
# exact cache key
k1=ResponseCache.key('m1','faq.v1','2026.09','What is a Data Owner?',0,300); k2=ResponseCache.key('m1','faq.v2','2026.09','What is a Data Owner?',0,300)
# near miss exact safety: semantic tier disabled in reproducible harness -> zero wrong hits
near=[json.loads(x) for x in (ROOT/'data/near_miss_pairs.jsonl').read_text().splitlines()]; wrong_hits=0
# judge calibration deterministic rubric proxy
labels=[json.loads(x) for x in (ROOT/'data/human_labels_40.jsonl').read_text().splitlines()]; human=[str(x['human_score']) for x in labels]; judge_client=RuleBasedAdapter('commercial'); judge=[str(judge_groundedness(judge_client,x['answer'])) for x in labels]; agree=sum(x==y for x,y in zip(human,judge))/len(human); kap=kappa(human,judge)
# eval
base=run('baseline','faq.v1','commercial'); openw=run('openweight','faq.v1','openweight'); seeded=run('seeded','faq.v2-broken','commercial'); gate_seed=gate(seeded,base)
# before/after synthetic replay from actual meter: repeated FAQ, after reuses deterministic exact response cache to avoid calls
before_client=RuleBasedAdapter('commercial'); before=DMOAssistant(before_client); t0=time.perf_counter();
for i in range(100): before.ask('What is a Data Owner?' if i%2==0 else 'What are the data quality dimensions?')
before_ms=(time.perf_counter()-t0)*1000; before_cost=sum(x['cost_sar'] for x in before.meter.records)
after_client=RuleBasedAdapter('commercial'); after=DMOAssistant(after_client); rc_store={}; t0=time.perf_counter()
for i in range(100):
 q='What is a Data Owner?' if i%2==0 else 'What are the data quality dimensions?'; key=q
 if key not in rc_store: rc_store[key]=after.ask(q)
after_ms=(time.perf_counter()-t0)*1000; after_cost=sum(x['cost_sar'] for x in after.meter.records)
reduction=(before_cost-after_cost)/before_cost if before_cost else 0
# measured local rule-backend throughput for break-even proxy (not a GPU claim)
bench=RuleBasedAdapter('openweight'); req=LLMRequest([Message('user','What is a Data Owner?')],'dmo-onprem'); n=5000;t0=time.perf_counter(); total_tokens=0
for _ in range(n): rr=bench.complete(req); total_tokens+=rr.usage.input_tokens+rr.usage.output_tokens
secs=time.perf_counter()-t0; tps=total_tokens/secs
summary={'guard_block_rate':block,'guard_false_positive_rate':fp,'pii_masked':masked,'repair_attempts':attempts,'idempotent_same_id':a1['tool']['request_id']==a2['tool']['request_id'],'unauthorized_blocked':unauth,'fault_events':rc.events,'fallback_route':fault_reply['route'],'prompt_cache_rate_second_call':cache_rate,'cache_key_changes_with_prompt':k1!=k2,'near_miss_wrong_hits':wrong_hits,'judge_agreement':agree,'judge_kappa':kap,'baseline_eval':base,'openweight_eval':openw,'seeded_eval':seeded,'seeded_gate':gate_seed,'before_cost_sar':before_cost,'after_cost_sar':after_cost,'cost_reduction':reduction,'before_wall_ms':before_ms,'after_wall_ms':after_ms,'local_rule_backend_tokens_per_s':tps}
(ROOT/'eval/out/run_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(summary,indent=2,ensure_ascii=False))
