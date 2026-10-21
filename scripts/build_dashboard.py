#!/usr/bin/env python3
"""Generate the static GitHub Pages dashboard from data/financial_data.json."""
import json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"financial_data.json"
DOCS=ROOT/"docs"
DOCS.mkdir(parents=True,exist_ok=True)
payload=json.loads(DATA.read_text(encoding="utf-8"))
(DOCS/"data.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")

HTML=r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="삼성전자 OpenDART 재무제표 및 재무비율 분석 대시보드">
<title>삼성전자 재무분석 대시보드 | DART Financial Intelligence</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
:root{--navy:#14263c;--ink:#1b2a3b;--muted:#728096;--line:#e3e9ef;--paper:#f3f6f9;--teal:#047e87;--blue:#4979bb;--gold:#c39a4a}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:14px/1.55 Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--teal);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1450px;margin:auto;padding:28px 25px 45px}
.hero{background:linear-gradient(125deg,#102238,#23576a);color:#fff;padding:34px 36px;border-radius:18px;position:relative;overflow:hidden;box-shadow:0 14px 34px #152c441c}
.hero:after{content:"";position:absolute;width:340px;height:340px;border:1px solid #ffffff1c;border-radius:50%;right:-75px;top:-155px;box-shadow:0 0 0 36px #ffffff08,0 0 0 72px #ffffff05}
.eyebrow{text-transform:uppercase;letter-spacing:.18em;font-size:10px;color:#aedce0;font-weight:850}
.hero h1{font-size:clamp(28px,4vw,42px);line-height:1.12;margin:12px 0 9px;letter-spacing:-.04em}
.hero p{color:#d5e2eb;max-width:780px;margin:0}
.hero-meta{display:flex;flex-wrap:wrap;gap:9px;margin-top:22px}.pill{border:1px solid #ffffff3d;border-radius:999px;padding:6px 11px;font-size:11px;color:#e5eef5}
.hero-nav{position:relative;z-index:1;margin-top:24px}.hero-nav a{display:inline-block;background:#fff;color:var(--navy);border-radius:8px;font-size:12px;font-weight:800;padding:9px 13px}
section{margin-top:30px}.section-head{display:flex;justify-content:space-between;align-items:flex-end;gap:14px;margin-bottom:14px}
.section-head h2{margin:0;font-size:20px;letter-spacing:-.025em}.section-head p{margin:4px 0 0;color:var(--muted);font-size:12px}
.updated{font-size:11px;color:var(--muted);text-align:right}.grid{display:grid;gap:14px}
.kpis{grid-template-columns:repeat(4,minmax(0,1fr))}.charts{grid-template-columns:repeat(2,minmax(0,1fr))}
.card{background:#fff;border:1px solid var(--line);border-radius:13px;box-shadow:0 2px 8px #18334b05}
.kpi{padding:19px 20px}.kpi label{color:var(--muted);font-size:11px;font-weight:750}
.kpi strong{display:block;font-size:clamp(22px,2.5vw,30px);letter-spacing:-.04em;margin:9px 0 4px;overflow-wrap:anywhere}
.kpi span{font-size:11px;color:var(--muted)}.chart-card{padding:18px 19px}.chart-card h3{font-size:14px;margin:0 0 4px}.chart-card p{margin:0 0 12px;color:var(--muted);font-size:11px}
.chart-wrap{height:260px;position:relative}.toolbar{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;padding:12px 15px;border-bottom:1px solid var(--line);color:var(--muted);font-size:11px}
.filter{border:1px solid var(--line);border-radius:7px;padding:8px 10px;width:170px;font:inherit;background:#fff}
.period-block{margin-top:21px}.period-title{display:flex;align-items:center;gap:9px;font-size:15px;font-weight:850;margin:0 0 9px;letter-spacing:-.01em}
.period-title span{color:var(--muted);font-size:11px;font-weight:500}
.table-card{overflow:hidden}.table-scroll{overflow:auto;max-width:100%}
table{width:100%;border-collapse:separate;border-spacing:0;font-variant-numeric:tabular-nums;white-space:nowrap}
th,td{padding:11px 12px;border-bottom:1px solid #edf1f5;text-align:right;font-size:11px}
th{background:#f6f9fb;color:#506176;font-weight:800;position:sticky;top:0;z-index:1}
th:first-child,td:first-child{text-align:left;position:sticky;left:0;background:#fff;z-index:2}
th:first-child{background:#f6f9fb;z-index:3}
tbody tr:hover td{background:#f5fafb}tbody tr:last-child td{border-bottom:0}
.empty{padding:35px 22px;text-align:center;color:var(--muted)}
.note{color:var(--muted);font-size:11px;line-height:1.7;margin:11px 2px 0}
.status{display:none;border:1px solid #eed7a7;background:#fff9e9;color:#815d21;border-radius:9px;padding:11px 14px;font-size:12px;margin-top:14px}.status.show{display:block}
.peer-table td:first-child,.peer-table td:nth-child(2){text-align:left}.peer-table td:nth-child(3),.peer-table td:nth-child(4){text-align:left;white-space:normal;min-width:200px}
.footer{display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px;margin-top:32px;padding-top:20px;border-top:1px solid var(--line);color:var(--muted);font-size:11px}
@media(max-width:940px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.charts{grid-template-columns:1fr}.wrap{padding:18px 13px 32px}.hero{padding:27px 23px}}
@media(max-width:520px){.section-head{display:block}.updated{text-align:left;margin-top:8px}.kpis{gap:8px}.kpi{padding:14px}.hero h1{font-size:30px}}
</style>
</head>
<body>
<main class="wrap">
<header class="hero">
 <div class="eyebrow">OpenDART · Financial Intelligence</div>
 <h1>Samsung Electronics<br>Financial Dashboard</h1>
 <p>삼성전자의 DART 공시 재무정보와 재무비율을 시각적으로 살펴봅니다. 공시 수치와 계산 지표를 구분하고, Annual · Half-year · Quarterly 자료 및 국내 비교기업을 한 화면에서 비교합니다.</p>
 <div class="hero-meta"><span class="pill">KOSPI · 005930</span><span class="pill">2015–present</span><span class="pill">KRW · OpenDART</span><span class="pill" id="latestPeriod">데이터 로딩 중</span></div>
 <div class="hero-nav"><a href="https://github.com/HSC-Class02/hy_samsung-electronics">Repository / Source files ↗</a></div>
</header>
<div id="statusWarning" class="status"></div>
<section>
 <div class="section-head"><div><h2>Executive Snapshot</h2><p>가장 최근 연간 사업보고서 기준 · 금액은 조원 단위</p></div><div id="updatedAt" class="updated">마지막 업데이트 확인 중</div></div>
 <div class="grid kpis">
  <article class="card kpi"><label>매출액 · REVENUE</label><strong id="kpiRevenue">—</strong><span id="kpiRevenueSub">매출 성장률 —</span></article>
  <article class="card kpi"><label>영업이익 · OPERATING INCOME</label><strong id="kpiOperating">—</strong><span id="kpiOperatingSub">영업이익률 —</span></article>
  <article class="card kpi"><label>당기순이익 · NET INCOME</label><strong id="kpiNet">—</strong><span id="kpiNetSub">순이익률 —</span></article>
  <article class="card kpi"><label>자산총계 · TOTAL ASSETS</label><strong id="kpiAssets">—</strong><span id="kpiAssetsSub">부채/자산 —</span></article>
 </div>
</section>
<section><div class="section-head"><div><h2>Trends & Financial Position</h2><p>연간 기준. 공시값이 확인되지 않은 항목은 임의로 채우지 않습니다.</p></div></div>
 <div class="grid charts">
  <article class="card chart-card"><h3>영업 실적</h3><p>매출액과 영업이익 · 조원</p><div class="chart-wrap"><canvas id="performanceChart"></canvas></div></article>
  <article class="card chart-card"><h3>재무상태</h3><p>자산·부채·자본 · 조원</p><div class="chart-wrap"><canvas id="balanceChart"></canvas></div></article>
  <article class="card chart-card"><h3>수익성</h3><p>영업이익률과 순이익률 · %</p><div class="chart-wrap"><canvas id="marginChart"></canvas></div></article>
  <article class="card chart-card"><h3>현금흐름</h3><p>영업활동 현금흐름과 잉여현금흐름 · 조원</p><div class="chart-wrap"><canvas id="cashChart"></canvas></div></article>
 </div>
</section>
<section>
 <div class="section-head"><div><h2>Financial Statements & Ratios</h2><p>요청에 따라 Annual, Half-year, Quarterly 수치표를 각각 표시합니다. 재무금액은 억원, 비율은 %입니다.</p></div></div>
 <div class="toolbar card"><span>기간별 재무수치 + 주요 비율</span><label>연도 필터 <input class="filter" id="yearFilter" placeholder="예: 2024"></label></div>
 <div class="period-block"><h3 class="period-title">Annual <span>사업보고서 · Year-end</span></h3><article id="annualTable" class="card table-card"><div class="empty">연간 데이터를 불러오는 중입니다.</div></article></div>
 <div class="period-block"><h3 class="period-title">Half-year <span>반기보고서 · First half</span></h3><article id="halfYearTable" class="card table-card"><div class="empty">반기 데이터를 불러오는 중입니다.</div></article></div>
 <div class="period-block"><h3 class="period-title">Quarterly <span>Q1, Q2, Q3, Q4 · Standalone quarters</span></h3><article id="quarterlyTable" class="card table-card"><div class="empty">분기 데이터를 불러오는 중입니다.</div></article></div>
 <p class="note">반기 표의 손익·현금흐름은 6개월 누적 값입니다. 분기 표의 Q2는 반기 누적값에서 Q1을 차감하고, Q4는 연간 값에서 Q1~Q3를 차감할 수 있을 때만 계산합니다. ROA·ROE·총자산회전율은 중간기간을 연환산하지 않습니다. ROIC는 세율 22%를 가정한 참고용 추정치이며 공시 수치가 아닙니다.</p>
</section>
<section>
 <div class="section-head"><div><h2>Domestic Peer Firms</h2><p>전자·반도체·디스플레이 생태계에 속한 국내 비교기업의 최근 연간 공시 기반 비교</p></div></div>
 <article id="peerTable" class="card table-card peer-table"><div class="empty">비교기업 정보를 불러오는 중입니다.</div></article>
 <p class="note">비교기업은 사업 구조가 완전히 동일하지 않은 참고군입니다. 삼성전자는 반도체·모바일·가전 등 복합 사업구조를 갖고 있으므로 각 기업의 사업 포트폴리오, 업황, 연결범위 및 회계 계정을 함께 고려해 비교하세요.</p>
</section>
<footer class="footer"><span>Source: OpenDART · Calculated ratios are estimates from published filing line items.</span><span><a href="https://github.com/HSC-Class02/hy_samsung-electronics">GitHub Repository</a> · <a href="https://opendart.fss.or.kr/">OpenDART</a></span></footer>
</main>
<script>
const METRICS=[
 ['revenue','매출액','amount'],['gross_profit','매출총이익','amount'],['operating_income','영업이익','amount'],['net_income','당기순이익','amount'],
 ['total_assets','자산총계','amount'],['total_liabilities','부채총계','amount'],['equity','자본총계','amount'],['current_assets','유동자산','amount'],['current_liabilities','유동부채','amount'],
 ['cash','현금및현금성자산','amount'],['receivables','매출채권','amount'],['inventory','재고자산','amount'],['interest_bearing_debt','이자부부채','amount'],['net_debt','순차입금','amount'],
 ['cfo','영업활동현금흐름','amount'],['cfi','투자활동현금흐름','amount'],['cff','재무활동현금흐름','amount'],['capex','CAPEX','amount'],['fcf','잉여현금흐름','amount'],
 ['gross_margin','매출총이익률','pct'],['operating_margin','영업이익률','pct'],['net_margin','순이익률','pct'],['ebitda_margin','EBITDA 마진','pct'],
 ['roa','ROA','pct'],['roe','ROE','pct'],['roic','ROIC*','pct'],['current_ratio','유동비율','multiple'],['debt_to_equity','부채/자본','multiple'],
 ['debt_to_assets','부채/자산','pct'],['equity_ratio','자기자본비율','pct'],['interest_coverage','이자보상배율','multiple'],['net_debt_ebitda','순차입금/EBITDA','multiple'],
 ['asset_turnover','총자산회전율','multiple'],['cfo_net_income','CFO/당기순이익','multiple'],['sales_growth','매출 성장률 YoY','pct'],['operating_income_growth','영업이익 성장률 YoY','pct']
];
let D=null,CHARTS=[];
const $=id=>document.getElementById(id);
const AMOUNT_KEYS=new Set(METRICS.filter(m=>m[2]==='amount').map(m=>m[0]));
const PCT_KEYS=new Set(METRICS.filter(m=>m[2]==='pct').map(m=>m[0]));
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function fmt(v,dp=1){return v===null||v===undefined||v===''||!Number.isFinite(Number(v))?'—':Number(v).toLocaleString('ko-KR',{minimumFractionDigits:0,maximumFractionDigits:dp});}
function eok(v){return v===null||v===undefined?'—':fmt(Number(v)/1e8,0);}
function trillion(v){return v===null||v===undefined?'—':fmt(Number(v)/1e12,2)+'조';}
function pct(v){return v===null||v===undefined?'—':fmt(Number(v)*100,2)+'%';}
function multiple(v){return v===null||v===undefined?'—':fmt(v,2)+'x';}
function value(v,type){return type==='amount'?eok(v):type==='pct'?pct(v):type==='multiple'?multiple(v):esc(v??'—');}
function renderKpis(){
 const a=(D.annual||[]).slice().sort((x,y)=>Number(x.year)-Number(y.year));const r=a[a.length-1];
 if(!r){$('latestPeriod').textContent='데이터 없음';return;}
 $('latestPeriod').textContent=r.year+'년 사업보고서';
 $('updatedAt').textContent='마지막 업데이트: '+(D.updated_at||'—').replace('T',' ').replace(/\.\d+Z?$/,' UTC');
 $('kpiRevenue').textContent=trillion(r.revenue);$('kpiRevenueSub').textContent='매출 성장률 '+pct(r.sales_growth);
 $('kpiOperating').textContent=trillion(r.operating_income);$('kpiOperatingSub').textContent='영업이익률 '+pct(r.operating_margin);
 $('kpiNet').textContent=trillion(r.net_income);$('kpiNetSub').textContent='순이익률 '+pct(r.net_margin);
 $('kpiAssets').textContent=trillion(r.total_assets);$('kpiAssetsSub').textContent='부채/자산 '+pct(r.debt_to_assets);
}
function renderTable(targetId,rows,label){
 const filter=($('yearFilter').value||'').trim();
 rows=(rows||[]).filter(r=>!filter||String(r.year).includes(filter)).slice().sort((a,b)=>Number(b.year)-Number(a.year)||(Number(b.quarter||0)-Number(a.quarter||0)));
 const target=$(targetId);
 if(!rows.length){target.innerHTML='<div class="empty">표시할 데이터가 없습니다. 인증키와 최신 Actions 실행 결과를 확인하세요.</div>';return;}
 const cols=[['label','기간','label'],...METRICS.map(m=>[m[0],m[1],m[2]]),['fs_div','재무제표','label'],['rcept_no','공시','link']];
 let html='<div class="toolbar"><span>'+label+' · '+rows.length+' periods</span><span>원 단위 수치를 억원으로 환산</span></div><div class="table-scroll"><table><thead><tr>'+cols.map(c=>'<th>'+c[1]+'</th>').join('')+'</tr></thead><tbody>';
 for(const r of rows){
  html+='<tr>'+cols.map(c=>{
   if(c[0]==='rcept_no')return '<td>'+(r.rcept_no?'<a target="_blank" rel="noopener" href="https://dart.fss.or.kr/dsaf001/main.do?rcpNo='+encodeURIComponent(r.rcept_no)+'">공시 ↗</a>':'—')+'</td>';
   if(c[0]==='label')return '<td>'+esc(r.label||r.period||r.year)+'</td>';
   if(c[0]==='fs_div')return '<td>'+esc(r.fs_div||'—')+'</td>';
   return '<td>'+value(r[c[0]],c[2])+'</td>';
  }).join('')+'</tr>';
 }
 target.innerHTML=html+'</tbody></table></div>';
}
function renderTables(){renderTable('annualTable',D.annual,'Annual · 사업보고서');renderTable('halfYearTable',D.half_year,'Half-year · 반기보고서');renderTable('quarterlyTable',D.quarterly,'Quarterly · 독립 분기 값');}
function renderPeers(){
 const p=D.peers||[];if(!p.length){$('peerTable').innerHTML='<div class="empty">Peer firm 자료가 없습니다.</div>';return;}
 const cols=[['company','기업'],['ticker','종목코드'],['segment','주요 사업'],['year','기준연도'],['revenue','매출액'],['operating_income','영업이익'],['net_income','당기순이익'],['operating_margin','영업이익률'],['roe','ROE'],['roa','ROA'],['roic','ROIC*'],['net_debt_ebitda','순차입금/EBITDA'],['rationale','비교 근거'],['caveat','비교 유의점'],['url','DART']];
 let h='<div class="table-scroll"><table><thead><tr>'+cols.map(c=>'<th>'+c[1]+'</th>').join('')+'</tr></thead><tbody>';
 for(const r of p){h+='<tr>'+cols.map(c=>{
  const k=c[0];
  if(k==='url')return '<td>'+(r.url?'<a href="'+esc(r.url)+'" target="_blank" rel="noopener">공시 ↗</a>':'—')+'</td>';
  if(['revenue','operating_income','net_income'].includes(k))return '<td>'+eok(r[k])+'</td>';
  if(['operating_margin','roe','roa','roic'].includes(k))return '<td>'+pct(r[k])+'</td>';
  if(k==='net_debt_ebitda')return '<td>'+multiple(r[k])+'</td>';
  return '<td>'+esc(r[k]??'—')+'</td>';
 }).join('')+'</tr>';}
 $('peerTable').innerHTML=h+'</tbody></table></div>';
}
function chart(id,type,labels,sets,fmtType){
 const ctx=$(id);if(!ctx)return;
 CHARTS.push(new Chart(ctx,{type,data:{labels,datasets:sets},options:{
  responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
  plugins:{legend:{labels:{usePointStyle:true,boxWidth:8,font:{size:10}}},tooltip:{callbacks:{label:c=>c.dataset.label+': '+(fmtType==='pct'?fmt(c.raw,2)+'%':trillion(c.raw))}}},
  scales:{x:{grid:{display:false},ticks:{font:{size:10}}},y:{grid:{color:'#edf1f5'},ticks:{font:{size:10},callback:v=>fmtType==='pct'?v+'%':(v/1e12).toFixed(1)}}}
 }}));
}
function renderCharts(){
 CHARTS.forEach(c=>c.destroy());CHARTS=[];
 const a=(D.annual||[]).slice().sort((x,y)=>Number(x.year)-Number(y.year));if(!a.length)return;
 const labels=a.map(r=>String(r.year));
 chart('performanceChart','line',labels,[
  {label:'매출액',data:a.map(r=>r.revenue),borderColor:'#087e87',backgroundColor:'#087e8718',fill:true,tension:.25,pointRadius:2},
  {label:'영업이익',data:a.map(r=>r.operating_income),borderColor:'#4979bb',tension:.25,pointRadius:2}
 ]);
 chart('balanceChart','bar',labels,[
  {label:'자산',data:a.map(r=>r.total_assets),backgroundColor:'#14263c'},
  {label:'부채',data:a.map(r=>r.total_liabilities),backgroundColor:'#047e87'},
  {label:'자본',data:a.map(r=>r.equity),backgroundColor:'#c39a4a'}
 ]);
 chart('marginChart','line',labels,[
  {label:'영업이익률',data:a.map(r=>r.operating_margin===null?null:r.operating_margin*100),borderColor:'#047e87',tension:.25,pointRadius:2},
  {label:'순이익률',data:a.map(r=>r.net_margin===null?null:r.net_margin*100),borderColor:'#c39a4a',tension:.25,pointRadius:2}
 ],'pct');
 chart('cashChart','bar',labels,[
  {label:'영업활동현금흐름',data:a.map(r=>r.cfo),backgroundColor:'#4979bb'},
  {label:'잉여현금흐름',data:a.map(r=>r.fcf),backgroundColor:'#047e87'}
 ]);
}
async function init(){
 try{
  const res=await fetch('./data.json',{cache:'no-store'});if(!res.ok)throw new Error('HTTP '+res.status);
  D=await res.json();renderKpis();renderCharts();renderTables();renderPeers();
  if(!D.annual?.length){$('statusWarning').className='status show';$('statusWarning').textContent='재무데이터가 아직 없습니다. Actions를 실행하고 DART_API_KEY를 확인하세요.';}
 }catch(e){$('statusWarning').className='status show';$('statusWarning').textContent='데이터 파일을 읽지 못했습니다: '+e.message+'. Actions에서 수집·분석·배포 상태를 확인하세요.';}
}
$('yearFilter').addEventListener('input',renderTables);
init();
</script>
</body></html>
"""
(DOCS/"index.html").write_text(HTML,encoding="utf-8")
print(f"Built {DOCS/'index.html'} and {DOCS/'data.json'}; annual={len(payload.get('annual',[]))}, half-year={len(payload.get('half_year',[]))}, quarterly={len(payload.get('quarterly',[]))}, peers={len(payload.get('peers',[]))}")
