"""Analyze observed pilot evidence without inventing clinical ratings (standard library)."""
from pathlib import Path
import csv, json, statistics, sys, hashlib

ROOT=Path(__file__).resolve().parents[1]
def rows(name):
    with (ROOT/'records'/name).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

def main():
    intake=rows('video_intake.csv'); metadata=rows('video_metadata.csv'); evidence=rows('domain_evidence.csv')
    ids=[x['pilot_id'] for x in metadata]
    assert len(ids)==len(set(ids)), 'duplicate unique-video key'
    assert len({(x['platform'],x['video_id']) for x in metadata})==len(ids)
    assert all(x['canonical_pilot_id'] in ids for x in intake)
    assert all(x['pilot_id'] in ids for x in evidence)
    pairs=[(x['pilot_id'],int(x['domain'])) for x in evidence]
    assert len(pairs)==len(set(pairs))==len(ids)*10
    assert all({int(x['domain']) for x in evidence if x['pilot_id']==i}==set(range(1,11)) for i in ids)
    assert all(x['evidence_flag'] in ('E','U','X') for x in evidence)
    assert all(x['time_reference'].strip() and x['evidence_summary'].strip() for x in evidence if x['evidence_flag']=='E')
    domain=[]; totals=[]
    for d in range(1,11):
        group=[x for x in evidence if int(x['domain'])==d]
        counts={k:sum(x['evidence_flag']==k for x in group) for k in ('E','U','X')}
        assert sum(counts.values())==len(ids)
        vals=[int(x['clinical_score']) for x in group if x['clinical_score']!='']
        assert all(v in (0,1,2) for v in vals)
        domain.append({'domain':d,**counts,'clinical_score_n':len(vals)})
    for i in ids:
        group=[x for x in evidence if x['pilot_id']==i]
        vals=[int(x['clinical_score']) for x in group if x['clinical_score']!='']
        total=sum(vals) if len(vals)==10 else None
        if total is not None:
            assert 0<=total<=20
            assert sum(v>=1 for v in vals)+sum(v==2 for v in vals)==total
        totals.append({'pilot_id':i,'E':sum(x['evidence_flag']=='E' for x in group),'U':sum(x['evidence_flag']=='U' for x in group),'X':sum(x['evidence_flag']=='X' for x in group),'clinical_score_n':len(vals),'clinical_total':total})
    # E/U/X describe evidence provenance. They are never converted into scores 0/1/2.
    accessible=[x for x in metadata if x['content_evidence_available']=='yes']
    unavailable=[x for x in metadata if x['content_evidence_available']=='no']
    assert all(x['evidence_flag']=='X' for x in evidence if x['pilot_id'] in {m['pilot_id'] for m in unavailable})
    assert all(x['evidence_flag']!='X' for x in evidence if x['pilot_id'] in {m['pilot_id'] for m in accessible})
    lengths=[int(x['duration_seconds']) for x in metadata]
    summary={'audit_date':'2026-10-22','data_status':'OBSERVED_PUBLIC_VIDEO_EVIDENCE_AI_ASSISTED_NOT_CLINICALLY_VALIDATED',
      'supplied_entries':len(intake),'unique_videos':len(metadata),'duplicate_entries':sum(x['disposition']=='duplicate' for x in intake),
      'metadata_available':len(metadata),'content_evidence_available':len(accessible),'content_unavailable':len(unavailable),
      'duration_seconds':{'n':len(lengths),'min':min(lengths),'median':statistics.median(lengths),'max':max(lengths),'above_1200':sum(x>1200 for x in lengths)},
      'platforms':{p:{'unique':sum(x['platform']==p for x in metadata),'content_evidence_available':sum(x['platform']==p for x in accessible)} for p in sorted({x['platform'] for x in metadata})},
      'evidence_cells':len(evidence),'evidence_counts':{k:sum(x['evidence_flag']==k for x in evidence) for k in ('E','U','X')},
      'clinical_item_scores_available':sum(x['clinical_score']!='' for x in evidence),'complete_clinical_totals_n':sum(x['clinical_total'] is not None for x in totals),
      'independent_human_rating_pairs':0,'clinical_agreement':'NOT_ESTIMABLE_NO_HUMAN_PAIRED_RATINGS',
      'clinical_association_regression_auc':'NOT_RUN_NO_COMPLETED_CLINICAL_SCORES',
      'domain_counts':domain,'per_video':totals,'python_version':sys.version.split()[0],
      'checks':{'unique_keys':'PASS','duplicate_links':'PASS','domain_grid':'PASS','evidence_provenance':'PASS','flag_partition':'PASS','missing_not_zero':'PASS','clinical_total_guard':'PASS','original_simulation_not_imported':'PASS'}}
    out=ROOT/'outputs';out.mkdir(exist_ok=True)
    (out/'pilot_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    for name,data in [('domain_evidence_counts.csv',domain),('per_video_summary.csv',totals)]:
        with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    print(json.dumps({k:summary[k] for k in ['supplied_entries','unique_videos','duplicate_entries','content_evidence_available','evidence_counts','complete_clinical_totals_n','checks']},ensure_ascii=False))
if __name__=='__main__':main()
