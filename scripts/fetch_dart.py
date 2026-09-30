import os,json,time,re
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
KEY=os.environ.get('DART_API_KEY','').strip()
if not KEY: raise SystemExit('DART_API_KEY secret is required.')
CFG=json.loads((ROOT/'config/companies.json').read_text(encoding='utf-8'))
REPORTS={'annual':'11011','half':'11012','q1':'11013','q3':'11014'}
YEAR_MAX=__import__('datetime').datetime.now().year
def amt(x):
 s=str(x).replace(',','').strip() if x is not None else ''
 try:return float(s) if s and s not in ('-','null','None') else None
 except:return None
def pick(rows,patterns):
 for pat in patterns:
  rx=re.compile(pat,re.I)
  for r in rows:
   if rx.search(r.get('account_nm','')):
    v=amt(r.get('thstrm_amount'))
    if v is not None:return v
 return None
def fetch(corp,year,code):
 p={'crtfc_key':KEY,'corp_code':corp,'bsns_year':year,'reprt_code':code,'fs_div':'CFS'}
 j=requests.get('https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json',params=p,timeout=30).json()
 if j.get('status')=='013':
  p['fs_div']='OFS';j=requests.get('https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json',params=p,timeout=30).json()
 return j.get('list',[]) if j.get('status')=='000' else []
def extract(rows):
 bs=[r for r in rows if r.get('sj_div')=='BS']; pl=[r for r in rows if r.get('sj_div') in ('IS','CIS')]; cf=[r for r in rows if r.get('sj_div')=='CF']; P=lambda g,p:pick(g,p)
 d={'total_assets':P(bs,[r'^자산총계$']),'cash':P(bs,[r'현금및현금성자산']),'receivables':P(bs,[r'매출채권']),'inventory':P(bs,[r'재고자산']),'current_assets':P(bs,[r'^유동자산$']),'current_liabilities':P(bs,[r'^유동부채$']),'total_liabilities':P(bs,[r'^부채총계$']),'equity':P(bs,[r'^자본총계$']),'short_borrowings':P(bs,[r'단기차입금','유동성장기차입금','유동성사채']),'long_borrowings':P(bs,[r'장기차입금','사채']),'revenue':P(pl,[r'^매출액$','^수익\(매출액\)$','^영업수익$']),'gross_profit':P(pl,[r'^매출총이익$']),'operating_income':P(pl,[r'^영업이익$','^영업이익\(손실\)$']),'pretax_income':P(pl,[r'법인세비용차감전순이익','세전이익']),'net_income':P(pl,[r'^당기순이익$','당기순이익\(손실\)']),'controlling_net_income':P(pl,[r'지배기업의 소유주에게 귀속되는 당기순이익']),'interest_expense':P(pl,[r'이자비용']),'depreciation':P(pl,[r'감가상각비']),'amortization':P(pl,[r'무형자산상각비','상각비']),'cfo':P(cf,[r'영업활동으로 인한 현금흐름','영업활동현금흐름']),'cfi':P(cf,[r'투자활동으로 인한 현금흐름','투자활동현금흐름']),'cff':P(cf,[r'재무활동으로 인한 현금흐름','재무활동현금흐름']),'capex_ppe':P(cf,[r'유형자산의 취득']),'capex_intangible':P(cf,[r'무형자산의 취득'])}
 if d['gross_profit'] is None and d['revenue'] is not None:
  c=P(pl,[r'매출원가']);d['gross_profit']=d['revenue']-c if c is not None else None
 d['ebitda']=d['operating_income']+(d['depreciation'] or 0)+(d['amortization'] or 0) if d['operating_income'] is not None else None
 cap=(d['capex_ppe'] or 0)+(d['capex_intangible'] or 0) if d['capex_ppe'] is not None or d['capex_intangible'] is not None else None
 d['capex']=abs(cap) if cap is not None else None;d['fcf']=d['cfo']-d['capex'] if d['cfo'] is not None and d['capex'] is not None else None
 debt=(d['short_borrowings'] or 0)+(d['long_borrowings'] or 0) if d['short_borrowings'] is not None or d['long_borrowings'] is not None else None
 d['interest_bearing_debt']=debt;d['net_debt']=debt-d['cash'] if debt is not None and d['cash'] is not None else None
 return d
out=[]
for c in [CFG['primary']]+CFG['peers']:
 for y in range(2010,YEAR_MAX+1):
  for period,code in REPORTS.items():
   try:
    rows=fetch(c['corp_code'],y,code)
    if rows:
     d=extract(rows);d.update({'company':c['name'],'corp_code':c['corp_code'],'ticker':c['ticker'],'year':y,'period':period,'source':'DART Open API'});out.append(d)
   except Exception as e: print('WARN',c['name'],y,period,e)
   time.sleep(.05)
(DATA/'dart_financials.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('saved',len(out))
