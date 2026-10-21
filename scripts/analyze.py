#!/usr/bin/env python3
"""Derive annual, half-year, standalone quarterly series and calculate financial ratios."""
from __future__ import annotations
import json, math
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
CFG=json.loads((ROOT/"config/companies.json").read_text(encoding="utf-8"))
FLOW={"revenue","gross_profit","operating_income","pretax_income","net_income","controlling_net_income",
      "interest_expense","depreciation","amortization","cfo","cfi","cff","capex_ppe","capex_intangible","ebitda","capex","fcf"}
FIELDS=["total_assets","cash","receivables","inventory","current_assets","current_liabilities","total_liabilities","equity",
        "short_borrowings","long_borrowings","revenue","gross_profit","operating_income","pretax_income","net_income",
        "controlling_net_income","interest_expense","depreciation","amortization","ebitda","cfo","cfi","cff",
        "capex_ppe","capex_intangible","capex","fcf","interest_bearing_debt","net_debt"]

def num(v):
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except (TypeError,ValueError):
        return None

def div(a,b):
    a,b=num(a),num(b)
    if a is None or b in (None,0): return None
    v=a/b
    return v if math.isfinite(v) else None

def base_values(record, ytd=False):
    d={}
    for k in FIELDS:
        source=k+"_ytd" if ytd and k in FLOW else k
        d[k]=num(record.get(source))
    # Net debt may need to be recomputed for an interim balance sheet if source fields exist.
    debt=d.get("interest_bearing_debt")
    cash=d.get("cash")
    d["net_debt"]=debt-cash if debt is not None and cash is not None else num(record.get("net_debt"))
    return d

def subtract(a,b):
    return a-b if a is not None and b is not None else None

def standalone_from_cumulative(cum, prior, template):
    out=dict(template)
    for k in FIELDS:
        if k in FLOW:
            out[k]=subtract(cum.get(k),prior.get(k)) if cum and prior else None
    return out

def make_quarter(template, year, q, label, values):
    r={"year":int(year),"quarter":q,"period":"quarterly","label":label,"rcept_no":template.get("rcept_no"),
       "fs_div":template.get("fs_div"),"source":template.get("source","DART OpenDART API")}
    for k in FIELDS:r[k]=num(values.get(k))
    return r

def ratio_fields(rows, kind, annual_by_year, half_by_year, quarter_by_year):
    rows=sorted(rows,key=lambda r:(r["year"],r.get("quarter") or 0))
    for r in rows:
        year=r["year"]; q=r.get("quarter")
        prior_balance=None; prior_yoy=None
        if kind=="annual":
            prior_balance=annual_by_year.get(year-1)
            prior_yoy=prior_balance
        elif kind=="half_year":
            prior_balance=annual_by_year.get(year-1)
            prior_yoy=half_by_year.get(year-1)
        else:
            prior_balance=annual_by_year.get(year-1) if q==1 else quarter_by_year.get((year,q-1))
            prior_yoy=quarter_by_year.get((year-1,q))
        assets=num(r.get("total_assets")); equity=num(r.get("equity"))
        p_assets=num(prior_balance.get("total_assets")) if prior_balance else None
        p_equity=num(prior_balance.get("equity")) if prior_balance else None
        avg_assets=(assets+p_assets)/2 if assets is not None and p_assets is not None else assets
        avg_equity=(equity+p_equity)/2 if equity is not None and p_equity is not None else equity
        rev=num(r.get("revenue")); op=num(r.get("operating_income")); ni=num(r.get("net_income"))
        gross=num(r.get("gross_profit")); ebitda=num(r.get("ebitda")); cfo=num(r.get("cfo"))
        debt=num(r.get("interest_bearing_debt")); cash=num(r.get("cash")); liabilities=num(r.get("total_liabilities"))
        interest=num(r.get("interest_expense"))
        # ROIC uses a disclosed 22% illustrative tax-rate assumption; actual tax expense is not modeled.
        invested=(avg_equity + debt - cash) if avg_equity is not None and debt is not None and cash is not None else None
        r.update({
          "gross_margin":div(gross,rev),
          "operating_margin":div(op,rev),
          "net_margin":div(ni,rev),
          "ebitda_margin":div(ebitda,rev),
          "roa":div(ni,avg_assets),
          "roe":div(ni,avg_equity),
          "current_ratio":div(r.get("current_assets"),r.get("current_liabilities")),
          "debt_to_equity":div(liabilities,equity),
          "debt_to_assets":div(liabilities,assets),
          "equity_ratio":div(equity,assets),
          "interest_coverage":div(op,interest),
          "net_debt_ebitda":div(r.get("net_debt"),ebitda),
          "asset_turnover":div(rev,avg_assets),
          "cfo_net_income":div(cfo,ni),
          "roic":div(op*0.78,invested) if op is not None and invested not in (None,0) else None,
        })
        pr=num(prior_yoy.get("revenue")) if prior_yoy else None
        pop=num(prior_yoy.get("operating_income")) if prior_yoy else None
        r["sales_growth"]=div(rev-pr,abs(pr)) if rev is not None and pr not in (None,0) else None
        r["operating_income_growth"]=div(op-pop,abs(pop)) if op is not None and pop not in (None,0) else None
    return rows

def enrich_periods(records, company):
    by={(int(r["year"]),r["period"]):r for r in records if r.get("company")==company["name"]}
    annual=[]; half=[]; qmap={}
    years=sorted({int(r["year"]) for r in records if r.get("company")==company["name"]})
    for year in years:
        ar=by.get((year,"annual"))
        hr=by.get((year,"half"))
        q1r=by.get((year,"q1"))
        q3r=by.get((year,"q3"))
        if ar:
            vals=base_values(ar)
            annual.append({"year":year,"period":"annual","label":str(year),"rcept_no":ar.get("rcept_no"),
                           "fs_div":ar.get("fs_div"),"source":ar.get("source"),**vals})
        if hr:
            vals=base_values(hr,ytd=True)
            half.append({"year":year,"period":"half_year","label":f"{year} H1","quarter":2,"rcept_no":hr.get("rcept_no"),
                         "fs_div":hr.get("fs_div"),"source":hr.get("source"),**vals})
        qmap.setdefault(year,{})
        if q1r:
            vals=base_values(q1r)
            qmap[year][1]=make_quarter(q1r,year,1,f"{year} Q1",vals)
        if hr:
            hvals=base_values(hr,ytd=True)
            prior_q1=qmap[year].get(1)
            if prior_q1:
                q2vals=dict(hvals)
                for k in FIELDS:
                    if k in FLOW:q2vals[k]=subtract(hvals.get(k),prior_q1.get(k))
            else:
                # The quarter cannot be inferred from a cumulative H1 amount without Q1 data.
                q2vals=dict(hvals)
                for k in FLOW:q2vals[k]=None
            qmap[year][2]=make_quarter(hr,year,2,f"{year} Q2",q2vals)
        if q3r:
            vals=base_values(q3r)
            # If reported quarter flow fields are empty, derive standalone Q3 from 9-month YTD less H1 YTD.
            hvals=base_values(hr,ytd=True) if hr else None
            yvals=base_values(q3r,ytd=True)
            for k in FLOW:
                if vals.get(k) is None and hvals is not None:
                    vals[k]=subtract(yvals.get(k),hvals.get(k))
            qmap[year][3]=make_quarter(q3r,year,3,f"{year} Q3",vals)
        if ar:
            annual_vals=base_values(ar)
            if all(q in qmap[year] for q in (1,2,3)):
                q4vals=dict(annual_vals)
                for k in FLOW:
                    parts=[qmap[year][q].get(k) for q in (1,2,3)]
                    q4vals[k]=annual_vals.get(k)-sum(parts) if annual_vals.get(k) is not None and all(x is not None for x in parts) else None
            else:
                q4vals=dict(annual_vals)
                for k in FLOW:q4vals[k]=None
            qmap[year][4]=make_quarter(ar,year,4,f"{year} Q4",q4vals)
    annual=sorted(annual,key=lambda r:r["year"])
    half=sorted(half,key=lambda r:r["year"])
    quarterly=[qmap[y][q] for y in sorted(qmap) for q in sorted(qmap[y])]
    annual_by={r["year"]:r for r in annual}
    half_by={r["year"]:r for r in half}
    quarter_by={(r["year"],r["quarter"]):r for r in quarterly}
    annual=ratio_fields(annual,"annual",annual_by,half_by,quarter_by)
    half=ratio_fields(half,"half_year",annual_by,half_by,quarter_by)
    quarterly=ratio_fields(quarterly,"quarterly",annual_by,half_by,quarter_by)
    return annual,half,quarterly

def main():
    raw=json.loads((DATA/"dart_financials.json").read_text(encoding="utf-8"))
    by_name={c["name"]:c for c in [CFG["primary"]]+CFG["peers"]}
    primary=CFG["primary"]
    annual,half,quarterly=enrich_periods(raw,primary)
    peers=[]
    for company in CFG["peers"]:
        a,h,q=enrich_periods(raw,company)
        if a: last=a[-1]
        elif h: last=h[-1]
        else: last={}
        peers.append({
          "company":company["name"],"ticker":company["ticker"],"segment":company.get("segment",""),
          "rationale":company.get("rationale",""),"caveat":company.get("caveat",""),
          "url":f"https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm={company.get('stock_code',company['ticker'].split('.')[0])}",
          "year":last.get("year"),"revenue":last.get("revenue"),"operating_income":last.get("operating_income"),
          "net_income":last.get("net_income"),"operating_margin":last.get("operating_margin"),
          "roe":last.get("roe"),"roa":last.get("roa"),"roic":last.get("roic"),
          "net_debt":last.get("net_debt"),"net_debt_ebitda":last.get("net_debt_ebitda"),
        })
    result={
      "company":{"name":primary["name"],"english_name":primary.get("english_name","Samsung Electronics Co., Ltd."),
                 "ticker":primary["ticker"],"stock_code":primary.get("stock_code","005930"),"corp_code":primary["corp_code"],
                 "market":"KOSPI","currency":"KRW"},
      "updated_at":datetime.now(timezone.utc).isoformat(),
      "data_start_year":2015,
      "units":{"raw_amount":"KRW","dashboard_amount":"억원","ratio":"%"},
      "annual":annual,"half_year":half,"quarterly":quarterly,"peers":peers,
      "methodology":{
        "financial_scope":"Consolidated statements (CFS) are preferred; standalone (OFS) is queried only when consolidated statements return no records.",
        "interim_reporting":"Half-year flow metrics use six-month cumulative values. Q2 is derived from H1 cumulative less Q1; Q4 is derived from annual less Q1-Q3 only when all component data exist.",
        "returns":"ROA/ROE and asset turnover are not annualized for interim periods.",
        "roic":"Illustrative ROIC uses NOPAT = operating income × (1 - 22% assumed tax rate); this is an analytical assumption, not reported tax guidance."
      }
    }
    out=DATA/"financial_data.json"
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
    print(f"Saved analysis: annual={len(annual)}, half_year={len(half)}, quarterly={len(quarterly)}, peer_firms={len(peers)}")

def self_test():
    assert div(10,2)==5 and div(10,0) is None
    assert subtract(5,2)==3 and subtract(None,2) is None
    template={"year":2025,"period":"annual","revenue":100,"total_assets":200,"equity":100,
              "operating_income":20,"net_income":10,"gross_profit":50,"ebitda":25,"cfo":15,
              "interest_bearing_debt":30,"cash":10,"total_liabilities":100}
    rows=ratio_fields([dict(template)],"annual",{2025:template},{},{})
    assert abs(rows[0]["operating_margin"]-.2)<1e-9
    assert len(CFG["peers"])>=3
    print("analyze self-test PASS")

if __name__=="__main__":
    import sys
    if "--self-test" in sys.argv:self_test()
    else:main()
