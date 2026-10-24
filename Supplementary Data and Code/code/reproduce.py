from pathlib import Path
import sys,subprocess,json,math,platform
import numpy as np
ROOT=Path(__file__).resolve().parent.parent
DEST=ROOT/'reproduced';DEST.mkdir(exist_ok=True)
subprocess.run([sys.executable,str(ROOT/'code/generate_simulated_package.py'),str(DEST/'original_outputs')],check=True)
subprocess.run([sys.executable,str(ROOT/'code/additional_analysis.py'),str(DEST/'original_outputs'),str(DEST/'additional_outputs')],check=True)
checked=0
def compare(a,b,path='root'):
 global checked
 if isinstance(a,dict):
  assert isinstance(b,dict) and a.keys()==b.keys(),path
  for k in a:compare(a[k],b[k],path+'/'+k)
 elif isinstance(a,list):
  assert isinstance(b,list) and len(a)==len(b),path
  for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i))
 elif isinstance(a,(int,float)) and not isinstance(a,bool):
  assert math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-10),(path,a,b)
  checked+=1
 else:assert a==b,(path,a,b)
for folder,name in [('original_outputs','SIMULATED_all_tables.json'),('additional_outputs','SIMULATED_additional_tables.json')]:
 compare(json.loads((ROOT/folder/name).read_text(encoding='utf-8')),json.loads((DEST/folder/name).read_text(encoding='utf-8')))
report=dict(status='passed',numeric_values_compared=checked,python=platform.python_version(),numpy=np.__version__,relative_tolerance=1e-9,absolute_tolerance=1e-10)
(DEST/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report),flush=True)
