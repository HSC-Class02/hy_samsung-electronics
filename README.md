# Samsung Electronics Financial Analysis Agent

[![🔗 대시보드 바로가기](https://img.shields.io/badge/🔗%20대시보드-바로가기-blue)](https://hsc-class02.github.io/hy_samsung-electronics/)

DART Open API를 이용해 삼성전자 사업보고서·반기보고서·분기보고서의 재무정보를 수집하고, 재무비율을 자동 계산하여 GitHub Pages 대시보드로 제공하는 프로젝트입니다.

## 핵심 기능
- 2010년부터 DART 공시 데이터 수집 시도
- 사업보고서(연간), 반기보고서, 1·3분기보고서 자동 수집
- 연결재무제표(CFS) 우선, 필요한 경우 별도재무제표(OFS) fallback
- 주요 재무수치: 매출액, 매출총이익, 영업이익, 세전이익, 당기순이익, 지배주주순이익, EBITDA 보조지표, 영업·투자·재무활동현금흐름, CAPEX, FCF, 순차입금
- 수익성·유동성·재무안정성·활동성·성장성·시장가치 관련 비율 자동 계산
- 연간 / 반기 / 분기 3개 표 제공
- 국내 비교기업 표 제공
- 매월 1일 GitHub Actions 자동 업데이트
- GitHub Pages 자동 배포

## DART API Key
GitHub 저장소의 **Settings → Secrets and variables → Actions → New repository secret**에서 다음 이름으로 입력합니다.

`DART_API_KEY`

API Key는 코드에 직접 입력하지 않습니다.

## 참고 기준
재무지표의 정의와 분석 흐름은 제공된 「재무제표 및 재무비율 실무 가이드」를 기준으로 구현했습니다. 단일 비율보다 성장→수익성→현금흐름→차입부담→투자수익률→시장평가의 연결을 중시합니다.

## 국내 비교기업
삼성전자의 사업구조를 고려한 비교기업으로 SK하이닉스, LG전자, 삼성전기, LG디스플레이를 기본 목록에 포함했습니다. 비교기업 데이터는 DART에서 제공되는 재무정보 범위 내에서 동일한 계산 규칙을 적용합니다.

## 주의
DART Open API가 제공하지 않는 과거 기간은 자동으로 억지로 채우지 않고 결측으로 표시합니다. 특히 2010~2014년은 API 제공 범위와 공시 구조에 따라 데이터가 없을 수 있습니다.
