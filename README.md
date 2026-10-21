# Samsung Electronics DART Financial Agent

[![🔗 대시보드 바로가기](https://img.shields.io/badge/🔗%20대시보드-바로가기-176B87?style=for-the-badge)](https://hsc-class02.github.io/hy_samsung-electronics/)

삼성전자(005930)의 OpenDART 공시 재무제표를 수집하고, 핵심 재무수치·재무비율을 계산해 GitHub Pages 대시보드로 보여주는 프로젝트입니다. 2010년부터 수집을 시도하며, Annual / Half-year / Quarterly 재무표를 각각 독립적으로 표시합니다.

## Dashboard

**[🔗 대시보드 바로가기](https://hsc-class02.github.io/hy_samsung-electronics/)** · [GitHub Actions](https://github.com/HSC-Class02/hy_samsung-electronics/actions) · [API 키 설정 안내](API_KEY_SETUP.md) · [OpenDART](https://opendart.fss.or.kr/)

## API 인증키 설정 및 최초 실행

1. [OpenDART](https://opendart.fss.or.kr/)에서 개인/기관 인증키를 발급받습니다. OpenDART 인증키는 보통 40자리입니다.
2. GitHub 저장소의 **Settings → Secrets and variables → Actions → New repository secret**으로 이동합니다.
3. Secret 이름을 정확히 **DART_API_KEY**로 입력하고, 발급받은 키를 Secret 값에 붙여 넣어 저장합니다.
4. **Settings → Pages → Build and deployment → Source**에서 **GitHub Actions**를 선택합니다.
5. **Actions → Samsung Electronics DART Financial Data Update & Deploy → Run workflow**를 실행합니다.
6. Actions에서 수집·분석·검증·배포 단계가 모두 성공했는지 확인합니다.

API 키는 소스코드나 이 README에 직접 기록하지 않습니다. GitHub Secret의 실제 값은 저장소 파일로 조회할 수 없으므로, 등록 여부는 설정 화면에서 확인하세요. 오류가 발생하면 Actions 로그의 OpenDART 오류 메시지를 확인하고, 인증키 오류인 경우 Secret 값을 새 키로 교체합니다.

## 자동 업데이트

GitHub Actions는 **매월 1일 한국시간 오전 9시**(UTC 00:00)에 실행됩니다. 워크플로가 OpenDART 자료 수집 → 재무비율 분석 → 데이터/대시보드 재생성 → 코드 검사 → GitHub Pages 배포를 순서대로 수행합니다. GitHub의 예약 실행은 플랫폼 부하에 따라 늦어질 수 있으며, Actions에서 수동 실행도 가능합니다.

## 주요 재무데이터

**기본 수치**
- 매출액, 매출총이익, 영업이익, 세전이익, 당기순이익, 지배기업 소유주 귀속 순이익
- 자산총계, 부채총계, 자본총계, 유동자산, 유동부채, 현금및현금성자산
- 매출채권, 재고자산, 차입금, 순차입금
- 영업·투자·재무활동 현금흐름, 자본적지출(CAPEX), 잉여현금흐름(FCF), EBITDA

**재무비율 및 성장률**
- 매출총이익률, 영업이익률, 순이익률, EBITDA 마진
- ROA, ROE, ROIC, 유동비율, 부채/자본, 부채/자산, 자기자본비율
- 이자보상배율, 순차입금/EBITDA, 총자산회전율, CFO/순이익
- 매출액 YoY, 영업이익 YoY

ROIC는 영업이익에 세율 22%를 적용한 NOPAT 가정을 사용하는 참고용 계산치입니다. 실제 세금 납부액 또는 회사의 공식 지표로 해석하지 마세요.

## 기간 구분 및 방법론

- DART 고유 법인코드: **00126380**, KOSPI 종목코드: **005930**.
- 연결재무제표(CFS)를 우선 사용하고, 연결 데이터가 조회되지 않을 때 별도재무제표(OFS)를 조회합니다. 각 데이터 행의 fs_div에서 기준을 확인할 수 있습니다.
- Annual은 연간 사업보고서, Half-year는 상반기 6개월 누적 손익·현금흐름, Quarterly는 Q1~Q4 단독 분기값입니다.
- Q2는 반기 누적값에서 Q1을 차감해 계산하고, Q4는 연간 값에서 Q1~Q3를 차감할 수 있는 경우에만 계산합니다. 필요한 구성 데이터가 없으면 해당 값은 공란(null)으로 남깁니다.
- ROA, ROE 및 총자산회전율은 중간기간에 대해 연환산하지 않습니다. YoY 성장률은 가능한 경우 동일한 기간을 비교합니다.
- Peer Firms는 사업구조가 서로 다른 국내 전자산업 참고군입니다. 규모·사업 포트폴리오·회계 분류가 다르므로 동일 업종의 완전한 대체 기업이나 투자 추천으로 간주하지 마세요.

## 국내 Peer Firms

| 기업 | 종목코드 | 주요 사업 | 비교 근거 | 비교 유의점 |
|---|---:|---|---|---|
| [SK하이닉스](https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=000660) | 000660 | 메모리 반도체 | 삼성전자 반도체 사업의 국내 핵심 비교군 | 메모리 사업 비중이 높음 |
| [LG전자](https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=066570) | 066570 | 가전·전장·전자제품 | 소비자 전자제품 및 전장 사업 비교 | 반도체 비중이 낮음 |
| [삼성전기](https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=009150) | 009150 | 전자부품·기판·MLCC | IT·전자 생태계의 주요 부품 공급사 | 부품 제조 중심 |
| [LG디스플레이](https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=034220) | 034220 | 디스플레이 패널 | 디스플레이 산업 및 패널 업황 비교 | 패널 가격과 투자 사이클 영향이 큼 |

Peer 표에는 최근 수집 가능한 연간 실적·수익성 지표를 함께 표시합니다. 비교 기준연도가 다를 수 있으므로 표의 연도를 반드시 확인하세요.

## 저장소 산출물

- data/dart_financials.json: OpenDART에서 수집한 재무 계정 및 기간별 값
- data/financial_data.json: 연간·반기·분기 데이터 및 계산된 비율
- docs/data.json: GitHub Pages가 읽는 대시보드 JSON
- docs/index.html: 그래프, 3개 재무 테이블, 하단 Peer Firms 테이블
- scripts/fetch_dart.py: DART 수집 및 응답 오류 처리
- scripts/analyze.py: Q2/Q4 단독 분기 계산, 재무비율 산출
- scripts/build_dashboard.py: 정적 대시보드 생성
- scripts/validate_project.py: 데이터·대시보드 구조 검사

## 저장소 About 링크

README 최상단에는 대시보드 배지를 넣었습니다. 저장소 오른쪽 About 섹션의 홈페이지 주소는 GitHub 설정에서 직접 저장해야 합니다.

1. 저장소 첫 화면의 **About** 옆 톱니바퀴를 클릭합니다.
2. Website에 https://hsc-class02.github.io/hy_samsung-electronics/ 를 입력합니다.
3. **Save changes**를 클릭합니다.

## 로컬 검사

Python 3.11 이상 권장:

    python -m pip install -r requirements.txt
    python -m py_compile scripts/fetch_dart.py scripts/analyze.py scripts/build_dashboard.py scripts/validate_project.py
    python scripts/fetch_dart.py --self-test
    python scripts/analyze.py --self-test

실제 수집은 환경변수 DART_API_KEY에 키를 등록한 후 python scripts/fetch_dart.py를 실행하세요. 키를 .env 파일에 저장하는 경우 해당 파일은 GitHub에 커밋하지 마세요.
