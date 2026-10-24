from pathlib import Path
import sys,json,csv,math
import numpy as np
ROOT=Path(__file__).resolve().parent.parent
BASE=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'original_outputs'
DATA=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'reproduced/additional_outputs'
DATA.mkdir(parents=True,exist_ok=True)
d=json.loads((BASE/'SIMULATED_all_tables.json').read_text(encoding='utf-8'))
t=d['tables'];meta=t['Metadata189'];final=t['FinalScores189']
assert [r['video_id'] for r in meta]==[r['video_id'] for r in final]
status='SIMULATED_NOT_OBSERVED';rng=np.random.default_rng(2026090801)
pairs=[]
for row in t['PairwiseDunn']:
 r=dict(row);a=np.array([v[r['measure']] for m,v in zip(meta,final) if m[r['grouping']]==r['first']]);b=np.array([v[r['measure']] for m,v in zip(meta,final) if m[r['grouping']]==r['second']])
 levels=np.unique(np.r_[a,b]);ca=np.array([(a==x).sum() for x in levels]);cb=np.array([(b==x).sum() for x in levels]);sgn=np.sign(levels[:,None]-levels[None,:])
 ba=rng.multinomial(len(a),ca/len(a),size=5000);bb=rng.multinomial(len(b),cb/len(b),size=5000)
 boot=np.sum((ba@sgn)*bb,axis=1)/(len(a)*len(b));lo,hi=np.quantile(boot,[.025,.975])
 assert abs((ca@sgn@cb)/(len(a)*len(b))-r['Cliffs_delta'])<1e-12
 r.update(delta_ci_low=float(lo),delta_ci_high=float(hi),ci_method='5000 independent within-group percentile bootstrap',ci_seed=2026090801)
 pairs.append(r)
platforms=['YouTube','TikTok','Bilibili','RedNote'];sources=['dentist','academic','commercial','other']
plats=np.array([r['platform'] for r in meta]);src=np.array([r['source'] for r in meta]);dur=np.array([r['duration_seconds'] for r in meta]);age=np.array([r['age_days'] for r in meta]);y=np.array([r['completeness_total'] for r in final])
X=np.column_stack([np.ones(189)]+[(plats==p).astype(float) for p in platforms[1:]]+[np.log2(dur)]+[(src==s).astype(float) for s in sources[1:]]+[np.log2(np.maximum(age,1))])
names=[r['predictor'] for r in t['RegressionHC3']]
vifs=[]
for j in range(1,9):
 xx=np.delete(X,j,axis=1);yy=X[:,j];e=yy-xx@np.linalg.lstsq(xx,yy,rcond=None)[0]
 vifs.append(dict(data_status=status,predictor=names[j],VIF=float(sum((yy-yy.mean())**2)/sum(e**2))))
assert abs(max(r['VIF'] for r in vifs)-t['ModelSummary'][0]['max_VIF'])<1e-12
flag=np.array([r['Cooks_distance']>4/189 for r in t['ModelDiagnostics']]);xx=X[~flag];yy=y[~flag];inv=np.linalg.inv(xx.T@xx);beta=inv@xx.T@yy;e=yy-xx@beta;h=np.sum((xx@inv)*xx,axis=1);cov=inv@(xx.T@((e**2/(1-h)**2)[:,None]*xx))@inv;se=np.sqrt(np.diag(cov));r2=1-sum(e**2)/sum((yy-yy.mean())**2)
sens=[dict(data_status=status,predictor=k,beta=float(b),HC3_se=float(s),ci_low=float(b-1.95996398454*s),ci_high=float(b+1.95996398454*s),p_normal_Wald=math.erfc(abs(b/s)/math.sqrt(2))) for k,b,s in zip(names,beta,se)]
sensinfo=dict(data_status=status,excluded_ids=[m['video_id'] for m,f in zip(meta,flag) if f],n=int(sum(~flag)),R_squared=float(r2),adjusted_R_squared=float(1-(1-r2)*(len(yy)-1)/(len(yy)-9)),criterion='Cook distance > 4/189 in the primary fit; exploratory deletion sensitivity only')
metadata=[]
for plat in ['all']+platforms:
 rows=[m for m in meta if plat=='all' or m['platform']==plat]
 for key in ['duration_seconds','age_days','views','likes','comments','view_rate_per_100_days']:
  val=np.array([r[key] for r in rows if r[key] is not None]);q=np.quantile(val,[.25,.5,.75])
  metadata.append(dict(data_status=status,platform=plat,measure=key,total_n=len(rows),valid_n=len(val),missing_n=len(rows)-len(val),q1=float(q[0]),median=float(q[1]),q3=float(q[2])))
pemat=[]
for scale,maxn in [('U',13),('A',4)]:
 key=f'PEMAT_{scale}_applicable_n'
 for denom in range(maxn+1):
  counts={r:sum(x[key]==denom for x in t['RawRatings378'] if x['rater_id']==r) for r in ['SIM_R1','SIM_R2']};counts['Final']=sum(x[key]==denom for x in final)
  if any(counts.values()):pemat.append(dict(data_status=status,scale=scale,applicable_items=denom,**counts))
extra=dict(data_status=status,seed=2026090801,bootstrap_resamples=5000,PairwiseWithCI=pairs,VIF=vifs,Sensitivity=sens,SensitivityInfo=sensinfo,MetadataSummary=metadata,PEMATDenominators=pemat)
(DATA/'SIMULATED_additional_tables.json').write_text(json.dumps(extra,ensure_ascii=False,indent=2),encoding='utf-8')
for key,rows in extra.items():
 if isinstance(rows,list) and rows and isinstance(rows[0],dict):
  with (DATA/f'SIMULATED_{key}.csv').open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

print('Additional numerical analyses complete.',flush=True)
