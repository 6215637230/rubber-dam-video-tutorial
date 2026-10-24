"""Synthetic teaching fixture. Never observed videos, raters or historical searches.
Run: python generate_simulated_package.py [output_directory]
Requires Python 3 and numpy. No fitted manuscript results or real identifiers.
"""
from pathlib import Path
import sys, json, csv, math, itertools, platform as pyplatform
import numpy as np

OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent/'SIMULATED_OUTPUT'
OUT.mkdir(parents=True,exist_ok=True)
STATUS='SIMULATED_NOT_OBSERVED'
SEED=2026090702
rng=np.random.default_rng(SEED); srng=np.random.default_rng(SEED+1)
B=5000; PERM=4999
platforms=['YouTube','TikTok','Bilibili','RedNote'];sizes=[48,42,50,49]
sources=['dentist','academic','commercial','other']
domains=['indications','armamentarium','clamp_selection','application','split_dam','isolation_configuration','sealing_inversion','stabilization','troubleshooting','removal']
dk=['D'+str(i+1).zfill(2) for i in range(10)]
spec=[('GQS',1,1,5),('mDISCERN',5,0,1),('JAMA',4,0,1),('PEMAT_U',13,0,1),('PEMAT_A',4,0,1),('VIQI',4,1,5),('D',10,0,2)]
itemkeys=[];bounds={}
for name,count,lo,hi in spec:
 for j in range(count):
  key=name if count==1 else (dk[j] if name=='D' else name+'_'+str(j+1).zfill(2))
  itemkeys.append(key);bounds[key]=(lo,hi)
source_labels=np.array(sum(([s]*n for s,n in zip(sources,[82,42,39,26])),[]));rng.shuffle(source_labels)
meta=[];raw=[];final=[];resolution=[]
def totals(items):
 out={'GQS':items['GQS']}
 for name,ct,lo,hi in spec[1:]:
  keys=dk if name=='D' else [name+'_'+str(j+1).zfill(2) for j in range(ct)]
  vals=[items[k] for k in keys if items[k] is not None]
  if name.startswith('PEMAT'):
   out[name+'_applicable_n']=len(vals);out[name+'_score']=None if not vals else 100*sum(vals)/len(vals)
  else:out['completeness_total' if name=='D' else name]=sum(vals)
 out['coverage_category']='comprehensive' if out['completeness_total']>=18 else ('basic' if out['completeness_total']>=12 else 'low')
 return out

for plat,n in zip(platforms,sizes):
 for j in range(n):
  i=len(meta);vid=f'SIM-{plat[:2].upper()}-{j+1:03d}'
  duration=int(rng.integers(15,1201));age=int(rng.integers(0,2001))
  views=int(rng.integers(0,100001));likes=int(rng.integers(0,1001));comments=int(rng.integers(0,101))
  if i==0:age=0
  if i==1:views=0
  if i%37==2:views=None
  if i%17==3:likes=None
  if i%13==4:comments=None
  if views is not None:
   if likes is not None:likes=min(likes,views)
   if comments is not None:comments=min(comments,views)
  m=dict(data_status=STATUS,video_id=vid,platform=plat,language='English' if plat in platforms[:2] else 'Mandarin',source=str(source_labels[i]),test_url=f'https://example.invalid/simulated-video/{vid}',title=f'SIMULATION ONLY rubber dam example {vid}',duration_seconds=duration,age_days=age,upload_day_offset=-age,extract_day_label='SIMULATED_DAY_0',views=views,likes=likes,comments=comments,view_rate_per_100_days=None if views is None else 100*views/max(age,1))
  meta.append(m)
  procedural_p=float(rng.uniform(0,1));generic_p=float(rng.uniform(.1,.9))
  base={}
  for k in itemkeys:
   lo,hi=bounds[k]
   if k.startswith('D'):value=int(rng.binomial(2,procedural_p))
   elif hi==1:value=int(rng.binomial(1,generic_p))
   else:value=int(rng.integers(lo,hi+1))
   if k.startswith('PEMAT') and not k.endswith('_01') and rng.random()<.08:value=None
   base[k]=value
  rater=[]
  for r in [1,2]:
   items={}
   for k,v in base.items():
    if v is None:items[k]=None;continue
    lo,hi=bounds[k]
    items[k]=int(rng.choice([x for x in range(lo,hi+1) if x!=v])) if rng.random()<.10 else v
   rater.append(items)
   raw.append(dict(data_status=STATUS,video_id=vid,rater_id='SIM_R'+str(r),**(items|totals(items))))
  consensus={}
  for k in itemkeys:
   a,b=rater[0][k],rater[1][k]
   if a==b:consensus[k]=a;continue
   mode='SIM_ADJUDICATION' if rng.random()<.2 else 'SIM_CONSENSUS'
   v=base[k] if mode=='SIM_ADJUDICATION' else [a,b][int(rng.integers(0,2))]
   consensus[k]=v
   resolution.append(dict(data_status=STATUS,video_id=vid,item=k,rater1=a,rater2=b,final=v,resolution_mode=mode,reviewer='SIM_R3' if mode=='SIM_ADJUDICATION' else 'SIM_R1_R2',time_label='SIMULATED_SCORING_STAGE'))
  final.append(dict(data_status=STATUS,video_id=vid,**(consensus|totals(consensus))))

# Artificial ranked records. No historical search dates, real URLs or real uploader identities.
terms_en=['rubber dam','rubber dam application','dental dam','dental isolation']
terms_zh=['橡皮障','橡皮障隔离','口腔隔离']
reason_options=['irrelevant','advertisement_no_instruction','image_only','duration_gt_20_min','primary_teeth_only','non_target_language','inaccessible']
logs=[];flow=[];manifest=[]
for pi,(plat,inc_n,unique_n) in enumerate(zip(platforms,sizes,[170,160,125,120])):
 terms=terms_en if pi<2 else terms_zh
 inc=[m for m in meta if m['platform']==plat]
 candidates={m['video_id']:dict(outcome='included',reason='',duration=m['duration_seconds'],url=m['test_url'],sponsor=bool(rng.random()<.08)) for m in inc}
 for i in range(unique_n-inc_n):
  key=f'SIM-{plat[:2].upper()}-EX-{i+1:03d}';reason=str(rng.choice(reason_options))
  candidates[key]=dict(outcome='excluded',reason=reason,duration=int(rng.integers(1201,3001)) if reason=='duration_gt_20_min' else (None if reason in ['image_only','inaccessible'] else int(rng.integers(15,1201))),url=f'https://example.invalid/simulated-video/{key}',sponsor=(True if reason=='advertisement_no_instruction' else bool(rng.random()<.08)))
 ids=list(candidates);draw=ids+list(rng.choice(ids,size=len(terms)*50-unique_n));rng.shuffle(draw)
 first={};local=[]
 for i,vid in enumerate(draw):
  obj=candidates[vid];rid=f'SIM-RETRIEVAL-{len(logs)+1:04d}';q=i//50;rank=i%50+1;dup=vid in first
  row=dict(data_status=STATUS,record_id=rid,platform=plat,query_id=f'SIM-Q{pi+1}-{q+1}',query=terms[q],rank=rank,query_time_label=f'SIMULATED_SESSION_{pi+1}_{q+1}',video_id=vid,test_url=obj['url'],first_record_id=first.get(vid,rid),screening_outcome='duplicate' if dup else obj['outcome'],primary_exclusion='duplicate_identifier' if dup else obj['reason'],sponsored=obj['sponsor'],counts_in_first50=True,duration_seconds=obj['duration'],sort_label='SIMULATED_DEFAULT_RELEVANCE',location_label='SIMULATED_US' if pi<2 else 'SIMULATED_CN',archive_status='NO_REAL_SEARCH_OR_ARCHIVE')
  first.setdefault(vid,rid);logs.append(row);local.append(row)
 for q,term in enumerate(terms):manifest.append(dict(data_status=STATUS,query_id=f'SIM-Q{pi+1}-{q+1}',platform=plat,query=term,retrieved=50,session_label=f'SIMULATED_SESSION_{pi+1}_{q+1}',setting='Artificial ranking; all sponsored slots count toward cap; no real browser or search run'))
 fl=dict(data_status=STATUS,platform=plat,retrieved=len(local),duplicates=sum(r['screening_outcome']=='duplicate' for r in local),screened=unique_n,included=inc_n,excluded=unique_n-inc_n)
 fl.update({reason:sum(r['screening_outcome']=='excluded' and r['primary_exclusion']==reason for r in local) for reason in reason_options});flow.append(fl)

def rank(a):
 _,ix,c=np.unique(a,return_inverse=True,return_counts=True);return (np.cumsum(c)-(c-1)/2)[ix]
def corr(a,b):
 a=np.array(a,dtype=float);b=np.array(b,dtype=float);ok=np.isfinite(a)&np.isfinite(b);a=a[ok];b=b[ok];n=len(a)
 def rho(x,y):return float(np.corrcoef(rank(x),rank(y))[0,1])
 obs=rho(a,b);ra=rank(a);rb=rank(b);ra-=ra.mean();rb-=rb.mean();den=np.linalg.norm(ra)*np.linalg.norm(rb)
 cnt=0
 for start in range(0,PERM,500):
  count=min(500,PERM-start);perm=srng.permuted(np.broadcast_to(rb,(count,n)),axis=1);cnt+=int(np.sum(abs(perm@ra/den)>=abs(obs)-1e-12))
 boot=[]
 for _ in range(B):
  ix=srng.integers(0,n,n)
  if np.ptp(a[ix]) and np.ptp(b[ix]):boot.append(rho(a[ix],b[ix]))
 lo,hi=np.quantile(boot,[.025,.975]);return dict(n=n,rho=obs,ci_low=float(lo),ci_high=float(hi),p_raw=(cnt+1)/(PERM+1),bootstrap_valid=len(boot))
def adjust(vals,method='BH'):
 a=np.array(vals);ix=np.argsort(a);v=a[ix];n=len(a)
 out=np.maximum.accumulate(v*(n-np.arange(n))) if method=='Holm' else np.minimum.accumulate((v*n/(np.arange(n)+1))[::-1])[::-1]
 answer=np.empty(n);answer[ix]=np.minimum(out,1);return answer.tolist()
def wilson(x,n):
 z=1.95996398454;p=x/n;den=1+z*z/n;c=(p+z*z/(2*n))/den;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;return c-h,c+h
keys=['GQS','mDISCERN','JAMA','PEMAT_U_score','PEMAT_A_score','VIQI','completeness_total']
vals={k:np.array([r[k] for r in final],dtype=float) for k in keys}
views=np.array([r['views'] for r in meta],dtype=float);rates=np.array([r['view_rate_per_100_days'] for r in meta],dtype=float);dur=np.array([r['duration_seconds'] for r in meta]);age=np.array([r['age_days'] for r in meta]);plats=np.array([r['platform'] for r in meta]);src=np.array([r['source'] for r in meta]);tot=vals['completeness_total'];gqs=vals['GQS']
descriptive=[]
for grouping,groups,labels in [('all',['all'],np.array(['all']*189)),('platform',platforms,plats),('source',sources,src)]:
 for g in groups:
  for name,arr in {**vals,'duration_seconds':dur,'age_days':age,'views':views,'view_rate_per_100_days':rates}.items():
   x=arr[labels==g];x=x[np.isfinite(x)];q=np.quantile(x,[.25,.5,.75]);descriptive.append(dict(data_status=STATUS,grouping=grouping,group=g,measure=name,n=len(x),mean=float(x.mean()),sd=float(x.std(ddof=1)),q1=float(q[0]),median=float(q[1]),q3=float(q[2])))
domain_stats=[]
for k,name in zip(dk,domains):
 x=np.array([r[k] for r in final]);a=int(sum(x>=1));b=int(sum(x==2));al,ah=wilson(a,189);bl,bh=wilson(b,189)
 domain_stats.append(dict(data_status=STATUS,domain=k,label=name,n0=int(sum(x==0)),n1=int(sum(x==1)),n2=b,n=189,any_n=a,any_proportion=a/189,any_ci_low=al,any_ci_high=ah,full_proportion=b/189,full_ci_low=bl,full_ci_high=bh))
correlations=[]
def addcorr(family,label,group,a,b):correlations.append(dict(data_status=STATUS,family=family,association=label,group=group,**corr(a,b)))
addcorr('Construct','GQS vs completeness','all',gqs,tot)
for name,y in [('GQS',gqs),('completeness',tot)]:addcorr('Popularity','view rate vs '+name,'all',rates,y)
addcorr('Secondary','duration vs completeness','all',dur,tot)
for p in platforms:
 mask=plats==p
 for name,a,b in [('view rate vs GQS',rates,gqs),('view rate vs completeness',rates,tot),('duration vs completeness',dur,tot)]:addcorr('Secondary',name,p,a[mask],b[mask])
for name,y in [('GQS',gqs),('completeness',tot)]:addcorr('Sensitivity','raw views vs '+name,'all',views,y)
for fam,method in [('Construct','None'),('Popularity','Holm'),('Secondary','BH'),('Sensitivity','BH')]:
 rows=[r for r in correlations if r['family']==fam];pp=[r['p_raw'] for r in rows];adj=pp if method=='None' else adjust(pp,method)
 for r,p in zip(rows,adj):r.update(p_adjusted=p,correction=method,family_size=len(rows))

# Two-way random, absolute-agreement, single-measure ICC; paired percentile bootstrap.
def icc2(a,b):
 x=np.column_stack([a,b]);n,k=x.shape;gm=x.mean();row=x.mean(axis=1);col=x.mean(axis=0)
 msr=k*sum((row-gm)**2)/(n-1);msc=n*sum((col-gm)**2)/(k-1);mse=np.sum((x-row[:,None]-col+gm)**2)/((n-1)*(k-1))
 den=msr+(k-1)*mse+k*(msc-mse)/n;return float((msr-mse)/den) if den else np.nan
def kappa(a,b,levels):
 mat=np.zeros((levels,levels));np.add.at(mat,(a.astype(int),b.astype(int)),1);mat/=len(a)
 disagreement=np.abs(np.arange(levels)[:,None]-np.arange(levels))/(levels-1)
 den=np.sum(disagreement*np.outer(mat.sum(axis=1),mat.sum(axis=0)));return 1-float(np.sum(mat*disagreement))/den if den else np.nan
reliability=[]
for key in keys+dk+['coverage_category']:
 a=np.array([r[key] for r in raw if r['rater_id']=='SIM_R1']);b=np.array([r[key] for r in raw if r['rater_id']=='SIM_R2'])
 if key=='coverage_category':
  code={'low':0,'basic':1,'comprehensive':2};a=np.array([code[x] for x in a]);b=np.array([code[x] for x in b])
 fun=(lambda x,y:kappa(x,y,3)) if key in dk+['coverage_category'] else icc2
 estimate=fun(a,b);boots=[]
 for _ in range(B):
  ix=srng.integers(0,189,189);v=fun(a[ix],b[ix])
  if np.isfinite(v):boots.append(v)
 low,high=np.quantile(boots,[.025,.975]);reliability.append(dict(data_status=STATUS,measure=key,n=189,method='linear_weighted_kappa' if key in dk+['coverage_category'] else 'ICC_2_1_absolute_single',estimate=estimate,ci_low=float(low),ci_high=float(high),ci_method='paired_percentile_bootstrap',valid_resamples=len(boots)))

omnibus=[];pairwise=[]
for grouping,groups,labels in [('platform',platforms,plats),('source',sources,src)]:
 for key,x in vals.items():
  ranks=rank(x);n=len(x);_,ct=np.unique(x,return_counts=True);tie=1-np.sum(ct**3-ct)/(n**3-n);counts={g:sum(labels==g) for g in groups};means={g:ranks[labels==g].mean() for g in groups}
  H=(12/(n*(n+1))*sum(counts[g]*means[g]**2 for g in groups)-3*(n+1))/tie
  # Exact survival function for chi-square with 3 degrees of freedom.
  p=math.erfc(math.sqrt(H/2))+math.sqrt(2*H/math.pi)*math.exp(-H/2)
  omnibus.append(dict(data_status=STATUS,grouping=grouping,measure=key,n=n,H=float(H),df=3,p_raw=p,epsilon_squared=max(0,(H-3)/(n-4))))
  rr=[]
  for a,b in itertools.combinations(groups,2):
   va=x[labels==a];vb=x[labels==b];z=(means[a]-means[b])/math.sqrt(n*(n+1)/12*tie*(1/counts[a]+1/counts[b]));pm=math.erfc(abs(z)/math.sqrt(2));delta=float(np.sign(va[:,None]-vb).mean())
   rr.append(dict(data_status=STATUS,grouping=grouping,measure=key,first=a,second=b,n_first=int(counts[a]),n_second=int(counts[b]),Dunn_z=float(z),p_raw=pm,Cliffs_delta=delta))
  for r,padj in zip(rr,adjust([r['p_raw'] for r in rr])):r.update(p_BH=padj,family_size=6)
  pairwise+=rr

X=np.column_stack([np.ones(189)]+[(plats==p).astype(float) for p in platforms[1:]]+[np.log2(dur)]+[(src==s).astype(float) for s in sources[1:]]+[np.log2(np.maximum(age,1))])
names=['Intercept','TikTok_vs_YouTube','Bilibili_vs_YouTube','RedNote_vs_YouTube','log2_duration','academic_vs_dentist','commercial_vs_dentist','other_vs_dentist','log2_age_bounded_1']
inv=np.linalg.inv(X.T@X);beta=inv@X.T@tot;resid=tot-X@beta;h=np.sum((X@inv)*X,axis=1);cov=inv@(X.T@((resid**2/(1-h)**2)[:,None]*X))@inv;se=np.sqrt(np.diag(cov));r2=1-sum(resid**2)/sum((tot-tot.mean())**2)
regression=[dict(data_status=STATUS,predictor=name,beta=float(b),HC3_se=float(s),ci_low=float(b-1.95996398454*s),ci_high=float(b+1.95996398454*s),p_normal_Wald=math.erfc(abs(b/s)/math.sqrt(2))) for name,b,s in zip(names,beta,se)]
vifs=[]
for j in range(1,X.shape[1]):
 xx=np.delete(X,j,axis=1);y=X[:,j];e=y-xx@np.linalg.lstsq(xx,y,rcond=None)[0];vifs.append(float(sum((y-y.mean())**2)/sum(e**2)))
cooks=resid**2/(sum(resid**2)/(189-X.shape[1]))*h/(X.shape[1]*(1-h)**2)
model=[dict(data_status=STATUS,n=189,slopes=8,residual_df=180,R_squared=float(r2),adjusted_R_squared=float(1-(1-r2)*188/180),max_VIF=max(vifs),max_leverage=float(max(h)),max_Cooks_distance=float(max(cooks)),cases_Cooks_gt_4_over_n=int(sum(cooks>4/189)),covariance='HC3',reference_distribution='normal_Wald_asymptotic')]
diagnostics=[dict(data_status=STATUS,video_id=r['video_id'],fitted=float(f),residual=float(e),leverage=float(l),Cooks_distance=float(c)) for r,f,e,l,c in zip(meta,X@beta,resid,h,cooks)]

positive=tot>=18;high=gqs>=4
tp=int(sum(positive&high));fp=int(sum(~positive&high));fn=int(sum(positive&~high));tn=int(sum(~positive&~high));npositive=tp+fn
roc=[]
for threshold in [6,5,4,3,2,1]:roc.append(dict(data_status=STATUS,threshold=threshold,sensitivity=float(sum((gqs>=threshold)&positive)/sum(positive)) if positive.any() else None,false_positive_rate=float(sum((gqs>=threshold)&~positive)/sum(~positive))))
def auc(pos,neg):return float(((pos[:,None]>neg)+.5*(pos[:,None]==neg)).mean())
pa=gqs[positive];na=gqs[~positive];av=auc(pa,na);ab=[auc(srng.choice(pa,len(pa)),srng.choice(na,len(na))) for _ in range(10000)];al,ah=np.quantile(ab,[.025,.975])
diag=[]
for name,a,b in [('sensitivity',tp,tp+fn),('specificity',tn,tn+fp),('PPV',tp,tp+fp),('NPV',tn,tn+fn)]:
 low,hi=wilson(a,b);diag.append(dict(data_status=STATUS,metric=name,estimate=a/b,ci_low=low,ci_high=hi,method='Wilson_95CI'))
odds=tp*tn/(fp*fn) if fp*fn else None
if min(tp,fp,fn,tn)>0:
 seod=math.sqrt(1/tp+1/fp+1/fn+1/tn);ol=math.exp(math.log(odds)-1.95996398454*seod);oh=math.exp(math.log(odds)+1.95996398454*seod)
else:ol=oh=None
prob=lambda k:math.comb(npositive,k)*math.comb(189-npositive,tp+fp-k)/math.comb(189,tp+fp)
allowed=range(max(0,tp+fp-(189-npositive)),min(npositive,tp+fp)+1);fisher=sum(prob(k) for k in allowed if prob(k)<=prob(tp)*(1+1e-12))
diag+=[dict(data_status=STATUS,metric='odds_ratio',estimate=odds,ci_low=ol,ci_high=oh,method='log_Wald_95CI'),dict(data_status=STATUS,metric='Fisher_two_sided_P',estimate=fisher,ci_low=None,ci_high=None,method='fixed_margins_exact'),dict(data_status=STATUS,metric='AUC',estimate=av,ci_low=float(al),ci_high=float(ah),method='10000_stratified_percentile_bootstrap')]
cross=[dict(data_status=STATUS,GQS_score=i,comprehensive=int(sum((gqs==i)&positive)),non_comprehensive=int(sum((gqs==i)&~positive)),total=int(sum(gqs==i))) for i in range(1,6)]

audit=[]
def check(name,ok,detail):
 audit.append(dict(data_status=STATUS,check=name,passed=bool(ok),detail=str(detail)));assert ok,name
check('included_189',len(meta)==len(final)==189,len(meta));check('raw_378',len(raw)==378,len(raw))
check('retrieved_700',len(logs)==700,len(logs));check('queries_14_each50',len(manifest)==14 and all(sum(r['query_id']==q['query_id'] for r in logs)==50 for q in manifest),len(manifest))
check('log_ids_match_final',{r['video_id'] for r in logs if r['screening_outcome']=='included'}=={r['video_id'] for r in meta},'one included upload per final row')
check('domain_total_identity',sum(r['any_n']+r['n2'] for r in domain_stats)==int(tot.sum()),int(tot.sum()))
check('classification_partition',sum(sum(r['coverage_category']==c for r in final) for c in ['low','basic','comprehensive'])==189,'all 189 classified')
check('zero_day_rate',meta[0]['view_rate_per_100_days']==100*meta[0]['views'],meta[0]['video_id'])
check('zero_views_zero_rate',meta[1]['view_rate_per_100_days']==0,meta[1]['video_id'])
check('missing_views_missing_rate',all((m['views'] is None)==(m['view_rate_per_100_days'] is None) for m in meta),'no zero imputation')
check('engagement_within_views',all(m['views'] is None or all(m[k] is None or m[k]<=m['views'] for k in ['likes','comments']) for m in meta),'synthetic counts bounded by known views')
check('all_item_ranges',all(r[k] is None or bounds[k][0]<=r[k]<=bounds[k][1] for r in raw+final for k in itemkeys),'all 41 synthetic items within declared ranges')
check('AUC_ROC_identity',abs(np.trapezoid([r['sensitivity'] for r in roc],[r['false_positive_rate'] for r in roc])-av)<1e-12,'pairwise and trapezoidal AUC match')
check('all_rows_simulated',all(r['data_status']==STATUS for r in meta+raw+final+logs+resolution),'explicit provenance every row')
for f in flow:check('flow_'+f['platform'],f['retrieved']==f['duplicates']+f['excluded']+f['included'] and f['excluded']==sum(f[k] for k in reason_options),f)
check('AUC_has_both_classes',len(pa)>0 and len(na)>0,f'{len(pa)} positive, {len(na)} negative')
for r in regression:check('coherent_HC3_'+r['predictor'],abs((r['ci_low']+r['ci_high'])/2-r['beta'])<1e-10,'same fit, normal reference')
print('SIMULATED ONLY:',len(meta),'videos;',len(raw),'rater rows;',len(logs),'retrieval rows; comprehensive=',len(pa),flush=True)
print('Simulation input generation complete. All statistical results computed from these inputs.',flush=True)

tables={'Metadata189':meta,'RawRatings378':raw,'FinalScores189':final,'ResolutionLog':resolution,'SearchLog700':logs,'QuerySettings14':manifest,'FlowSummary':flow,'Descriptive':descriptive,'DomainCoverage':domain_stats,'Reliability':reliability,'Correlations':correlations,'Omnibus':omnibus,'PairwiseDunn':pairwise,'RegressionHC3':regression,'ModelSummary':model,'ModelDiagnostics':diagnostics,'GQS_Crosstab':cross,'DiagnosticAccuracy':diag,'ROC_Coordinates':roc,'Audit':audit}
dictionary=[]
for name,rows in tables.items():
 for key in rows[0]:
  desc='See generation and statistical methods in README.'
  if key=='data_status':desc='Always SIMULATED_NOT_OBSERVED; no real observation.'
  if key=='video_id':desc='Artificial join key; never a real platform identifier.'
  if key in bounds:desc=f'Synthetic item rating; allowed {bounds[key][0]} to {bounds[key][1]}'+('; blank means not applicable' if key.startswith('PEMAT') else '')
  if key in dk:desc+='; '+domains[dk.index(key)]
  if key=='test_url':desc='Reserved example.invalid domain; deliberately not an actual video URL.'
  if key=='view_rate_per_100_days':desc='100*views/max(age_days,1); missing views gives missing rate.'
  if key=='primary_exclusion':desc='One simulated primary reason per first-seen rejected record; no historical screening occurred.'
  dictionary.append(dict(data_status=STATUS,table=name,field=key,description=desc))
tables['Dictionary']=dictionary
def default(x):return x.item() if isinstance(x,np.generic) else str(x)
for name,rows in tables.items():
 with open(OUT/f'SIMULATED_{name}.csv','w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'SIMULATED_all_tables.json').write_text(json.dumps(dict(data_status=STATUS,seed=SEED,statistics_seed=SEED+1,tables=tables),ensure_ascii=False,indent=2,default=default),encoding='utf-8')
readme=f'''# 模拟数据包 非真实观察

本包包含189条人工视频记录、378行双评者逐项评分、最终分数、逐项解决分歧日志、700行示例检索记录、14个示例查询以及统计输出。没有访问或观看真实视频，没有进行真实检索或专家评分。所有链接使用保留域名example.invalid，所有时间为SIMULATED标签。不得将本包标作真实原始数据、研究附件或实际历史检索日志。

## 生成原则
本次是新的完整模拟，不延续上一包的具体数值。种子={SEED}，统计随机种子={SEED+1}。仅固定总样本189、平台48/42/50/49、来源82/42/39/26，以及14查询×50条。独立抽取每视频procedural_p~Uniform(0,1)，各域基准分~Binomial(2,p)；generic_p~Uniform(.1,.9)，通用二元条目~Bernoulli(p)，GQS与VIQI基准为各自整数范围均匀抽取。元数据与评分不按原稿方向或显著性调参。没有拟合原稿的均值、相关、分类数量或P值。

双评者分别以10%概率将每个非缺失基准条目改为另一有效值。PEMAT每子量表第一项始终适用，其余条目8%概率不适用；双方及最终分数使用同一适用性。遇到分歧，80%走模拟共识（随机取两者之一），20%走模拟第三评者（取生成时基准值）。这些是软件生成机制，不是实际专家决策。Rater totals仅作原始评分派生汇总；最终总分从FinalScores189的最终条目重新计算。最终GQS为整数，PEMAT分别按适用条目计算百分数。

检索示例不是2026年6月1日的重建：示例独立ID数为170/160/125/120，重复记录125条、首次排除386条、纳入189条。随机分配查询排名；每个重复ID保留首次出现，重复记录链接first_record_id。每条首次排除仅有一个模拟原因。广告位置计入50条上限；商业/赞助状态并不自动排除带教学内容的纳入示例。纯广告的排除理由是advertisement_no_instruction。没有真实账号、地区设置、截图或历史时间戳。

## 统计方法与单位
描述统计均值/样本SD、中位数及numpy线性分位数IQR；时长为秒，年龄为天，view rate为每100天观看量。通用量表与总分在各平台及来源分组分别输出。逐域比例用Wilson95%区间。Kruskal–Wallis含秩并列校正，P用df=3卡方参考分布；Dunn含并列校正、双侧正态P，每个结局/分组的全部6对BH校正，Cliff's delta方向为第一组高于第二组。共7个结局×2种分组=84个配对结果。

Spearman使用平均秩；P由{PERM}次随机置换的加一校正获得，区间由{B}次成对percentile bootstrap获得。单独GQS–完整性为一个测试；2项归一化观看量为Holm族；13项分平台/时长为BH族；2项raw views为BH敏感性族。缺失观看量采用成对有效记录，不补零。置换P不应与原稿近似P逐位比较。

各通用量表及总分的ICC为双向随机效应、绝对一致性、单测量ICC(2,1)；10个域和3分类采用线性权重kappa。95%区间由{B}次成对percentile bootstrap获得。重采样单元为视频；原始评分用于一致性，不用最终共识分数。区间不是F分布型ICC区间。

模型为OLS完整性~平台+log2(duration)+来源+log2(max(age,1))；参考YouTube/dentist，8个斜率和截距，HC3协方差，双侧正态Wald推断。输出所有系数/SE/CI/P、R²、调整R²、VIF、leverage和Cook距离。模型P明确为渐近正态，非t分布。诊断CSV允许进一步作图，不宣称通过临床或模型有效性验证。

探索性诊断以GQS≥4预测完整性≥18。敏感度/特异度/PPV/NPV采用Wilson95%区间，OR采用log-Wald区间（零格时不强加校正），Fisher双侧固定边际精确检验，AUC按完整整数GQS且高分预测阳性、并列计0.5，10000次按结局分层bootstrap计算区间。分组交叉表和ROC坐标随附。

## 可复现性
运行 python generate_simulated_package.py <新的输出目录>，需要Python3和numpy。生成程序保留所有CSV及JSON，Excel中的统计值是这些代码输出的静态快照；更改Excel原始条目不会自动重跑统计分析。FinalScores189的量表总分/分类及Metadata189的view rate另以Excel公式提供。正式分析必须换入真实观察、真实搜索记录和经确认的评分规则。

版本 Python {pyplatform.python_version()}，numpy {np.__version__}。全部一致性检查通过；模拟全面覆盖{len(pa)}条，均值{tot.mean():.4f}，AUC {av:.4f}。这些数字仅描述本次模拟，不属于论文研究结果。
'''
(OUT/'README_模拟数据说明.md').write_text(readme,encoding='utf-8')
print(json.dumps({'output':str(OUT),'tables':len(tables),'audit_passed':all(r['passed'] for r in audit),'raw_item_columns':len(itemkeys),'resolution_rows':len(resolution)},ensure_ascii=False),flush=True)
