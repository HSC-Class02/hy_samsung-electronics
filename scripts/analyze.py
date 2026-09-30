import json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data';rows=json.loads((DATA/'dart_financials.json').read_text(encoding='utf-8'));df=pd.DataFrame(rows)
def n(x): return float(x) if pd.notna(x) else None
def div(a,b): return a/b if a is not None and b not in (None,0) else None
def calc(g):
 g=g.sort_values('year');out=[]
 for _,r in g.iterrows():
  prev=g[(g.year==r.year-1)&(g.period=='annual')];pa=prev.iloc[0] if len(prev) else None
  aa=(n(pa.total_assets)+n(r.total_assets))/2 if pa is not None and n(pa.total_assets) is not None and n(r.total_assets) is not None else n(r.total_assets)
  ae=(n(pa.equity)+n(r.equity))/2 if pa is not None and n(pa.equity) is not None and n(r.equity) is not None else n(r.equity)
  d={k:n(r[k]) for k in r.index if k not in ['company','corp_code','ticker','year','period','source']};d.update({'company':r.company,'year':int(r.year),'period':r.period,'label':str(int(r.year)) if r.period=='annual' else f"{int(r.year)} {'H1' if r.period=='half' else r.period.upper()}"})
  rev=n(r.revenue);op=n(r.operating_income);ni=n(r.net_income);gp=n(r.gross_profit);eb=n(r.ebitda);cfo=n(r.cfo);debt=n(r.interest_bearing_debt);cash=n(r.cash)
  d.update({'gross_margin':div(gp,rev),'operating_margin':div(op,rev),'net_margin':div(ni,rev),'ebitda_margin':div(eb,rev),'roa':div(ni,aa),'roe':div(ni,ae),'current_ratio':div(n(r.current_assets),n(r.current_liabilities)),'debt_ratio':div(n(r.total_liabilities),n(r.equity)),'equity_ratio':div(n(r.equity),n(r.total_assets)),'interest_coverage':div(op,n(r.interest_expense)),'net_debt_ebitda':div(n(r.net_debt),eb),'asset_turnover':div(rev,aa),'cfo_net_income':div(cfo,ni),'sales_growth':div(rev,n(pa.revenue))-1 if pa is not None and n(pa.revenue) not in (None,0) else None})
  invested=(ae or 0)+(debt or 0)-(cash or 0) if ae is not None and debt is not None and cash is not None else None;d['roic']=div(op*(1-.22),invested);out.append(d)
 return out
primary=df[df.company=='삼성전자'];res={'updated_at':pd.Timestamp.utcnow().isoformat(),'annual':calc(primary[primary.period=='annual']),'half_year':calc(primary[primary.period=='half']),'quarterly':calc(primary[primary.period.isin(['q1','q3'])]),'peers':[]}
for c,g in df.groupby('company'):
 if c!='삼성전자':
  a=calc(g[g.period=='annual'])
  if a:res['peers'].append({k:a[-1].get(k) for k in ['company','year','revenue','operating_income','net_income','operating_margin','roe','roa','roic','net_debt','net_debt_ebitda']})
(DATA/'financial_data.json').write_text(json.dumps(res,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
