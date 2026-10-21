#!/usr/bin/env python3
"""Collect Samsung Electronics and domestic peer financial statements from OpenDART."""
from __future__ import annotations
import io, json, os, re, sys, time, math, zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
CONFIG=json.loads((ROOT/"config/companies.json").read_text(encoding="utf-8"))
API="https://opendart.fss.or.kr/api"
YEAR_START=2010
REPORT_CODES=(("annual","11011"),("half","11012"),("q1","11013"),("q3","11014"))
FLOW_FIELDS={"revenue","gross_profit","operating_income","pretax_income","net_income","controlling_net_income","interest_expense","depreciation","amortization","cfo","cfi","cff","capex_ppe","capex_intangible"}
SESSION=requests.Session()

class DartAPIError(RuntimeError):
    pass

def amount(value):
    if value is None: return None
    s=str(value).replace(",","").strip()
    if not s or s.lower() in {"-","—","–","null","none","n/a"}: return None
    negative=s.startswith("(") and s.endswith(")")
    if negative: s=s[1:-1]
    try:
        value=float(s)
        return -value if negative else value
    except ValueError:
        return None

def normalize(text):
    return re.sub(r"[\s()（）\[\]{}·,./_-]","",str(text or "")).lower()

def value_for(row, mode):
    keys=("thstrm_add_amount","thstrm_amount") if mode=="ytd" else ("thstrm_amount","thstrm_add_amount")
    return next((v for v in (amount(row.get(k)) for k in keys) if v is not None),None)

def pick(rows, patterns, mode="period"):
    """Pick the best account match, respecting pattern priority and reporting line."""
    compiled=[re.compile(p,re.I) for p in patterns]
    for rx in compiled:
        for row in rows:
            name=str(row.get("account_nm","")).strip()
            if rx.search(name):
                val=value_for(row,mode)
                if val is not None:
                    return val
    return None

def sum_matching(rows, names, mode="period"):
    wanted={normalize(x) for x in names}
    vals=[]
    for row in rows:
        if normalize(row.get("account_nm","")) in wanted:
            v=value_for(row,mode)
            if v is not None: vals.append(v)
    return sum(vals) if vals else None

def get_json(endpoint, params):
    try:
        response=SESSION.get(f"{API}/{endpoint}.json",params=params,timeout=60)
        response.raise_for_status()
        result=response.json()
    except Exception as e:
        raise DartAPIError(f"OpenDART HTTP/JSON error for {endpoint}: {e}") from e
    status=str(result.get("status",""))
    if status=="000":
        return result.get("list",[]) or []
    if status=="013":
        return []
    message=str(result.get("message",""))
    if status in {"010","011","100","101"} or "인증키" in message:
        raise DartAPIError(f"OpenDART authentication/parameter error ({status}): {message}. Confirm the DART_API_KEY repository secret.")
    if status=="020":
        raise DartAPIError(f"OpenDART daily/request limit reached ({status}): {message}. Retry on a later run.")
    raise DartAPIError(f"OpenDART API error ({status}): {message}")

def parse_corp_directory(xml_bytes):
    """Return stock_code -> (corp_code, official name) from OpenDART's corpCode.xml."""
    root=ET.fromstring(xml_bytes)
    by_stock={}
    for row in root.findall(".//list"):
        stock=(row.findtext("stock_code") or "").strip()
        code=(row.findtext("corp_code") or "").strip()
        name=(row.findtext("corp_name") or "").strip()
        if stock and code:
            by_stock[stock]=(code,name)
    return by_stock

def resolve_corp_codes(companies):
    """Resolve current OpenDART legal codes by each listed firm's six-digit stock code."""
    try:
        response=SESSION.get(f"{API}/corpCode.xml",params={"crtfc_key":KEY},timeout=120)
        response.raise_for_status()
        archive_bytes=response.content
        if not zipfile.is_zipfile(io.BytesIO(archive_bytes)):
            try:
                error_xml=ET.fromstring(archive_bytes)
                detail=f" OpenDART status={error_xml.findtext('status')}; message={error_xml.findtext('message')}"
            except Exception:
                detail=f" Response excerpt: {response.text[:180].replace(chr(10),' ')}"
            raise DartAPIError("OpenDART corporate-code directory is not a ZIP. Check API authentication and availability."+detail)
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            member=next((name for name in archive.namelist() if name.lower().endswith("corpcode.xml")),archive.namelist()[0])
            by_stock=parse_corp_directory(archive.read(member))
    except DartAPIError:
        raise
    except Exception as exc:
        raise DartAPIError(f"Unable to download OpenDART corporate-code directory: {exc}") from exc
    for company in companies:
        stock=(company.get("stock_code") or company.get("ticker","").split(".")[0]).strip()
        match=by_stock.get(stock)
        if not match:
            print(f"WARNING: no OpenDART code match for {company['name']} / stock code {stock}; using configured code.")
            continue
        code,official_name=match
        old=company.get("corp_code")
        if old!=code:
            print(f"Resolved DART code for {company['name']} ({stock}): {old} -> {code} [{official_name}]")
        company["corp_code"]=code
    return companies

def fetch_report(corp_code, year, report_code):
    base={"crtfc_key":KEY,"corp_code":corp_code,"bsns_year":str(year),"reprt_code":report_code}
    rows=get_json("fnlttSinglAcntAll",{**base,"fs_div":"CFS"})
    if rows: return rows,"CFS"
    rows=get_json("fnlttSinglAcntAll",{**base,"fs_div":"OFS"})
    if rows: return rows,"OFS"
    return [],None

def extract(rows):
    bs=[r for r in rows if r.get("sj_div")=="BS"]
    pl=[r for r in rows if r.get("sj_div") in ("IS","CIS")]
    cf=[r for r in rows if r.get("sj_div")=="CF"]
    out={}
    # Balance-sheet values are point-in-time period-end balances, not cumulative.
    bs_patterns={
      "total_assets":[r"^자산총계$"],
      "cash":[r"^현금및현금성자산$",r"현금및현금성자산"],
      "receivables":[r"^매출채권$",r"매출채권"],
      "inventory":[r"^재고자산$",r"재고자산"],
      "current_assets":[r"^유동자산$"],
      "current_liabilities":[r"^유동부채$"],
      "total_liabilities":[r"^부채총계$"],
      "equity":[r"^자본총계$"],
    }
    for key,patterns in bs_patterns.items(): out[key]=pick(bs,patterns,"period")
    out["short_borrowings"]=sum_matching(bs,["단기차입금","유동성장기차입금","유동성사채"])
    out["long_borrowings"]=sum_matching(bs,["장기차입금","장기사채","사채"])
    # Statement flows are retained both as the current reporting period and, where provided,
    # the year-to-date cumulative amount. This lets the analyzer derive standalone Q2 and Q4.
    patterns={
      "revenue":([r"^매출액$",r"^수익\(매출액\)$",r"^영업수익$"],pl),
      "gross_profit":([r"^매출총이익$"],pl),
      "operating_income":([r"^영업이익$",r"^영업이익\(손실\)$"],pl),
      "pretax_income":([r"^법인세비용차감전순이익$",r"^세전이익$"],pl),
      "net_income":([r"^당기순이익$",r"^당기순이익\(손실\)$"],pl),
      "controlling_net_income":([r"지배기업의 소유주에게 귀속되는 당기순이익"],pl),
      "interest_expense":([r"^이자비용$",r"^금융원가$",r"^금융비용$"],pl),
      "depreciation":([r"감가상각비",r"감가상각"],pl),
      "amortization":([r"무형자산상각비",r"무형자산 상각"],pl),
      "cfo":([r"영업활동으로 인한 현금흐름",r"영업활동현금흐름",r"영업활동으로부터의 순현금흐름"],cf),
      "cfi":([r"투자활동으로 인한 현금흐름",r"투자활동현금흐름"],cf),
      "cff":([r"재무활동으로 인한 현금흐름",r"재무활동현금흐름"],cf),
      "capex_ppe":([r"유형자산의 취득",r"유형자산 취득"],cf),
      "capex_intangible":([r"무형자산의 취득",r"무형자산 취득"],cf),
    }
    for key,(regexes,group) in patterns.items():
        out[key]=pick(group,regexes,"period")
        out[key+"_ytd"]=pick(group,regexes,"ytd")
        if out[key+"_ytd"] is None: out[key+"_ytd"]=out[key]
    # A few issuers present cost of sales but not gross profit.
    if out.get("gross_profit") is None and out.get("revenue") is not None:
        cogs=pick(pl,[r"^매출원가$"],"period")
        cytd=pick(pl,[r"^매출원가$"],"ytd")
        out["gross_profit"]=out["revenue"]-cogs if cogs is not None else None
        out["gross_profit_ytd"]=out["revenue_ytd"]-cytd if cytd is not None and out["revenue_ytd"] is not None else out["gross_profit"]
    out["ebitda"]=out["operating_income"]+(out.get("depreciation") or 0)+(out.get("amortization") or 0) if out["operating_income"] is not None else None
    out["ebitda_ytd"]=out["operating_income_ytd"]+(out.get("depreciation_ytd") or 0)+(out.get("amortization_ytd") or 0) if out["operating_income_ytd"] is not None else None
    cap=[out.get("capex_ppe"),out.get("capex_intangible")]
    cap_ytd=[out.get("capex_ppe_ytd"),out.get("capex_intangible_ytd")]
    out["capex"]=abs(sum(v for v in cap if v is not None)) if any(v is not None for v in cap) else None
    out["capex_ytd"]=abs(sum(v for v in cap_ytd if v is not None)) if any(v is not None for v in cap_ytd) else out["capex"]
    out["fcf"]=out["cfo"]-out["capex"] if out.get("cfo") is not None and out.get("capex") is not None else None
    out["fcf_ytd"]=out["cfo_ytd"]-out["capex_ytd"] if out.get("cfo_ytd") is not None and out.get("capex_ytd") is not None else None
    debt=(out.get("short_borrowings") or 0)+(out.get("long_borrowings") or 0) if out.get("short_borrowings") is not None or out.get("long_borrowings") is not None else None
    out["interest_bearing_debt"]=debt
    out["net_debt"]=debt-out["cash"] if debt is not None and out.get("cash") is not None else None
    return out

def run():
    global KEY
    KEY=(os.environ.get("DART_API_KEY") or os.environ.get("OPENDART_API_KEY") or "").strip()
    if not KEY:
        raise DartAPIError("DART_API_KEY repository secret is not set. Add it under Settings → Secrets and variables → Actions.")
    if len(KEY)!=40:
        print(f"WARNING: DART_API_KEY has length {len(KEY)}; OpenDART keys are commonly 40 characters. The actual API response will determine whether this key is valid.")
    records=[]
    year_max=datetime.now().year
    companies=[dict(CONFIG["primary"]),*map(dict,CONFIG["peers"])]
    companies=resolve_corp_codes(companies)
    primary_name=CONFIG["primary"]["name"]
    for company in companies:
        print(f"Collecting {company['name']} ({company['ticker']})")
        # Full period history is needed to derive Q2/Q4 for Samsung Electronics.
        # Peer firms need annual observations for the comparison table, reducing API volume.
        reports_for_company=REPORT_CODES if company["name"]==primary_name else (("annual","11011"),)
        for year in range(YEAR_START,year_max+1):
            for period,code in reports_for_company:
                try:
                    rows,fs=fetch_report(company["corp_code"],year,code)
                except DartAPIError:
                    # Invalid credentials / API limit should stop the run immediately instead of producing
                    # hundreds of misleading empty periods.
                    raise
                except Exception as exc:
                    print(f"WARN {company['name']} {year} {period}: {exc}")
                    continue
                if rows:
                    record=extract(rows)
                    record.update({"company":company["name"],"corp_code":company["corp_code"],"ticker":company["ticker"],
                                   "year":year,"period":period,"fs_div":fs,"rcept_no":rows[0].get("rcept_no"),"source":"DART OpenDART API"})
                    records.append(record)
                time.sleep(0.05)
    DATA.mkdir(parents=True,exist_ok=True)
    target=DATA/"dart_financials.json"
    target.write_text(json.dumps(records,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
    print(f"Saved {len(records)} report-period records to {target.relative_to(ROOT)}")

def self_test():
    assert amount("1,234")==1234
    assert amount("(1,234)") == -1234
    assert amount("-") is None
    assert normalize(" 매출액 (손실) ")=="매출액손실"
    xml=b'<result><list><corp_code>00126371</corp_code><corp_name>Samsung Electro-Mechanics</corp_name><stock_code>009150</stock_code></list></result>'
    assert parse_corp_directory(xml)["009150"][0]=="00126371"
    test=[{"account_nm":"매출액","thstrm_amount":"100","thstrm_add_amount":"300","sj_div":"IS"}]
    assert pick(test,[r"^매출액$"],"period")==100
    assert pick(test,[r"^매출액$"],"ytd")==300
    print("fetch_dart self-test PASS")

if __name__=="__main__":
    if "--self-test" in sys.argv: self_test()
    else:
        try: run()
        except DartAPIError as exc:
            print(f"ERROR: {exc}",file=sys.stderr)
            raise SystemExit(1)
