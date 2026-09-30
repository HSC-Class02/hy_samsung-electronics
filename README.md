# Samsung Electronics Financial Analysis Agent

[![🔗 대시보드 바로가기](https://img.shields.io/badge/🔗%20대시보드-바로가기-blue)](https://hsc-class02.github.io/hy_samsung-electronics/)

DART Open API로 삼성전자 및 국내 비교기업의 사업·반기·분기 재무정보를 수집하고 재무비율을 계산하여 GitHub Pages 대시보드로 제공합니다.

## 기능
- 2010년부터 DART 데이터 수집 시도
- 사업보고서 / 반기보고서 / 1·3분기보고서
- 연결재무제표(CFS) 우선, OFS fallback
- 매출액·매출총이익·영업이익·순이익·CFO·CAPEX·FCF·순차입금 등
- 영업이익률·ROA·ROE·ROIC·유동비율·부채비율·이자보상배율·순차입금/EBITDA 등
- Annual / Half-year / Quarterly 표
- 국내 비교기업: SK하이닉스, LG전자, 삼성전기, LG디스플레이
- 매월 1일 GitHub Actions 자동 업데이트
- GitHub Pages 자동 배포

## DART API Key 설정
**Settings → Secrets and variables → Actions → New repository secret**에서 \`DART_API_KEY\`를 생성하고 DART Open API 키를 입력하세요. 키를 소스코드에 넣지 않습니다.

## 참고 기준
제공된 「재무제표 및 재무비율 실무 가이드」의 정의와 분석 순서를 기준으로 구현했습니다. 재무상태표·손익계산서·현금흐름표를 연결하고, 평균 자산·평균 자본을 사용하는 ROA·ROE 등 핵심 비율을 계산합니다.

DART API가 제공하지 않는 기간은 결측으로 남깁니다. 특히 2010~2014년은 API 제공 범위에 따라 데이터가 없을 수 있습니다.
