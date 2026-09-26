# KTX 예매난 위험도 분석 및 대체 이동수단 선택 AI 비서
> 제출용 README 빈칸 채우기 템플릿  
> 과제: **AI Agent 개발: 나만의 AI 비서 구축**

---

## README 사용 방법

이 문서는 과제 요구사항을 빠뜨리지 않도록 만든 **제출용 README 초안 + 체크리스트**입니다.

- **[AI 작성 완료]**: 현재까지 정해진 내용으로 초안을 채운 부분입니다.
- **[사용자 작성 필요]**: 실제 구현 결과, URL, 파일명, 수치처럼 직접 확인해야 하는 부분입니다.
- **[권장]**: 과제 필수는 아니지만 완성도와 평가 대응에 도움이 되는 부분입니다.
- 실제 제출 전에는 **구현하지 않은 기능을 구현했다고 쓰지 말고**, 완료된 내용만 남기세요.
- API Key, Firebase Private Key, 서비스 계정 JSON 원문은 README와 스크린샷에 절대 넣지 마세요.

---

## 현재 진행 단계

- [x] VS Code 프로젝트 폴더 생성: `ktx-congestion-analysis`
- [x] 제출용 README 초안 추가
- [x] 기본 폴더 구조 생성 (`backend`, `frontend`, `data/raw`, `data/processed`, `docs/images`, `scripts`)
- [x] Python 가상환경(`venv`) 생성 및 활성화 확인 (`(venv)` 프롬프트 확인)
- [x] `backend/requirements.txt` 패키지 설치 완료
- [x] `.gitignore` 파일명 교정 완료 및 `venv/` 제외 확인 (`git check-ignore -v venv/`)
- [x] Git 저장소 초기화 (`git init`) 및 `main` 브랜치 확인
- [x] KTX 핵심 데이터 1차 확보
- [x] 철도 시간대 패턴 보조 데이터 확보 (24시간대)
- [x] 원본 CSV 3개를 `data/raw`에 영문 파일명으로 배치
- [x] 원본 데이터(`raw`)와 가공 데이터(`processed`) 분리 및 가공 CSV 생성
- [x] 데이터 100개 이상 확보 여부 확인 (핵심 CSV 6,953행)
- [x] `preprocess_data.py` 1차 Code Review 반영 후 실행 성공
- [x] `ktx_demand.csv` 생성 확인 (**13,906행 × 7열**)
- [x] `rail_hourly_pattern_2025.csv` 생성 확인 (**72행 × 3열**)
- [x] `preprocess_data.py` 2차 Code Review 소규모 개선 반영 및 재실행
- [x] 전처리 완료 상태 첫 Git Commit (`feat: preprocess KTX demand data`)
- [x] `analyze_data.py` 작성 및 실행 성공
- [x] `analysis_summary.json` 생성 확인 및 실제 수치 검증
- [x] `station_summary.csv` 생성 확인
- [x] `analyze_data.py` Code Review 내용 검토
- [x] `analyze_data.py` Code Review 유효 개선사항 반영 및 재실행
- [x] Firestore 업로드용 `monthly_summary.csv` 생성 및 실제 검증 완료 (**168행 × 3열**)
- [x] VS Code Rainbow CSV 확장 설치 (편의 기능, 과제 필수 아님)
- [x] 분석 단계 두 번째 Git Commit (`feat: add KTX demand analysis summary`, commit `e79ec21`)
- [x] Firebase 프로젝트 생성 완료 (`ktx-congestion-analysis`, Spark 요금제)
- [x] Gemini in Firebase 사용 안 함
- [x] Google Analytics 사용 안 함
- [x] Google 개발자 프로그램 가입 선택 해제
- [x] Cloud Firestore Database 생성 완료 (`Standard`, `(default)`, `asia-northeast3 (Seoul)`, Production mode)
- [x] 로컬 비밀키 전용 `secrets/` 폴더 생성
- [x] `.gitignore`의 `secrets/` 제외 규칙 확인 (`git check-ignore -v --no-index` 성공)
- [x] Firebase `서비스 계정 > Firebase Admin SDK` 화면 도달 및 `새 비공개 키 생성` 버튼 확인
- [x] Firebase 서비스 계정 비공개 키 JSON 생성 및 `secrets/firebase-service-account.json`으로 보관
- [x] 서비스 계정 JSON Git 제외 확인 (`git check-ignore -v` 성공)
- [x] `GOOGLE_APPLICATION_CREDENTIALS` 환경변수 설정 및 경로 확인
- [x] Python Firebase Admin SDK → Firestore 연결 테스트 성공 (`현재 컬렉션 수: 0`)
- [x] `seed_firestore.py` 작성 및 Code Review 2 검토 완료
- [x] `seed_firestore.py` 실행 성공 (`data` 컬렉션 168건 업로드)
- [x] Firestore 업로드 검증 성공 (`target_documents=168`)
- [x] Firebase Console에서 `data` 컬렉션 및 대표 문서 필드 확인
- [x] `코드리뷰어.txt` 추가 제언 검토 완료 (선택 개선, 현재 추가 수정 불필요)
- [x] Firestore 단계 세 번째 Git Commit 완료 (`feat: seed Firestore with KTX monthly data`, commit `1e12ae2`)
- [ ] 세 번째 Commit 이후 최종 `git status` 확인 (Commit 직전 `frontend/`가 Untracked로 보였으므로 확인 필요)
- [ ] FastAPI 로컬 실행
- [x] Firestore 연결 및 초기 데이터 적재 완료 (`data` 컬렉션 168문서)
- [ ] GPT Context Injection 구현
- [ ] Frontend 구현
- [ ] Render / Vercel 배포
- [ ] 보너스 기능 및 최종 README 정리

> **다음 작업:** 세 번째 Git Commit `1e12ae2`까지 정상 완료했습니다. 다만 Commit 직전 `git status`에서 **`frontend/`가 Untracked files로 남아 있었기 때문에**, 아직 `nothing to commit, working tree clean`이라고 확정할 수는 없습니다. 먼저 `git status`를 다시 실행하고, `frontend/`가 남아 있으면 내부 파일을 확인한 뒤 필요한 파일인지 판단합니다. 작업 트리가 정리되면 **FastAPI Backend 기본 구조 생성**으로 넘어갑니다.

---

## 지금 할 일 — 세 번째 Commit 후 Git 상태 최종 확인

현재 실제 확인된 Commit 기록:

```text
1e12ae2 feat: seed Firestore with KTX monthly data
e79ec21 feat: add KTX demand analysis summary
7ea252b feat: preprocess KTX demand data
```

세 번째 Commit 자체는 정상 완료했습니다.

다만 **Commit 직전 `git status`에서 `frontend/`가 Untracked files로 표시**되어 있었습니다.

따라서 아직 아래 상태라고 단정하지 않습니다.

```text
nothing to commit, working tree clean
```

### 1) 지금 바로 최종 Git 상태 확인

```powershell
git status
```

#### A. 아래처럼 나오면 완전히 정상

```text
On branch main
nothing to commit, working tree clean
```

이 경우 바로 FastAPI Backend 단계로 넘어갑니다.

#### B. `frontend/`가 계속 보이면

예:

```text
Untracked files:
  frontend/
```

이 경우 **바로 `git add frontend/` 하지 말고**, 먼저 무엇이 들어 있는지 확인합니다.

```powershell
Get-ChildItem .\frontend -Force -Recurse
```

현재 Frontend 구현은 아직 시작하지 않았으므로,
의도하지 않은 임시 파일이라면 삭제하고,
향후 사용할 기본 파일이라면 내용을 확인한 뒤 Commit 여부를 결정합니다.

> Git은 완전히 빈 폴더 자체는 추적하지 않습니다.  
> 따라서 `frontend/`가 Untracked로 보인다면 그 안에 최소 하나 이상의 파일이 있다는 뜻입니다.

### 2) 작업 트리가 깨끗해진 뒤 다음 단계

다음은 **FastAPI Backend 기본 구조 생성**입니다.

우선 구현 순서:

```text
backend/main.py
→ backend/models/
→ backend/services/firestore_service.py
→ backend/services/data_service.py
→ backend/routers/data.py
→ FastAPI 로컬 실행
→ Swagger /docs 확인
→ /api/data CRUD
→ /api/data/summary
```

### 3) 다음 Commit은 언제?

FastAPI 앱 초기화와 `/docs` 실행까지 확인한 후
다음 Git Commit을 만드는 편이 좋습니다.

예상 Commit 단위:

```text
feat: initialize FastAPI backend
```

> 아직 GPT API, conversations, Frontend는 건드리지 않습니다.
> 먼저 Firestore 기반 Data API를 안정적으로 완성합니다.

---

## Claude Code Review 반영 기록

첨부한 Code Review 이미지를 기준으로 `preprocess_data.py`의 장점과 개선사항을 검토했습니다.

### 확인된 장점

- 입력/출력 경로와 파일명을 분리해 관리
- 필수 컬럼 검사 함수 사용
- 여러 한글 CSV 인코딩을 순차적으로 처리
- 보조 시간대 파일이 없어도 핵심 KTX 전처리를 계속할 수 있는 방어적 처리
- Wide → Long 변환으로 Firestore/분석에 사용하기 쉬운 구조 생성
- 처리 단계가 명확하고 변수명이 비교적 이해하기 쉬움

### 이번에 반영하는 개선

1. `print()` 대신 표준 `logging` 사용
2. 상행/하행 변환 중복 코드를 `DIRECTION_MAP`과 공통 함수로 통합
3. 프로젝트 경로를 `DataPaths` 설정 객체로 한 곳에서 관리
4. 날짜 및 숫자 변환 실패 시 원인을 이해하기 쉬운 `ValueError` 제공
5. `memo`는 제거하지 않음
   - 이번 과제의 기본 데이터 구조가 `(date, value, memo)`이므로
   - Firestore CRUD 및 AI Context에 설명 정보를 제공하는 용도로 유지

### 2차 Code Review 추가 검토

추가 리뷰에서 다음 제안이 확인되었습니다.

| 추가 제안 | 결정 | 이유 |
|---|---|---|
| `logging.basicConfig()`를 실행 시점으로 이동 | **반영** | 다른 모듈에서 import할 때 전역 로깅 설정에 미치는 영향을 줄임 |
| `memo`를 f-string + `apply()`로 변경 | **미반영** | 현재 벡터화 방식이 더 빠르고 충분히 명확함 |
| 요일 매핑을 `DAY_TYPE_MAP`으로 상수화 | **반영** | `DIRECTION_MAP`과 구조를 맞춰 일관성 향상 |

### 반영 원칙

> 외부 Code Review는 참고하되, **과제 요구사항·실제 데이터 구조와 충돌하지 않는 제안만 채택**합니다.

## analyze_data.py Code Review 검토

첨부한 `analyze_data.py 코드 리뷰.jpg`의 내용을 확인했습니다.

### 잘 된 점

- 추세 판단 임계값을 `TREND_THRESHOLD_PCT`로 분리
- `previous_12_avg == 0` 상황을 처리하여 ZeroDivisionError 방어
- `period`, `record_count`, `value_stats`, `monthly_total`, `recent_trend`처럼 구조화된 JSON Summary 생성
- 시간대 보조자료 부재 시 핵심 KTX 분석을 계속하는 방어적 처리
- 분석 결과가 API/System Prompt에서 바로 쓰기 좋은 구조

### Code Review 개선 제안과 결정

| 제안 | 결정 | 이유 |
|---|---|---|
| `require_columns()`를 공통 `utils.py`로 분리 | **추후 반영** | 중복 제거에는 좋지만 Backend 공통 유틸리티 작성 시 함께 정리 |
| `12`, `24` 매직 넘버 상수화 | **반영** | 추세 기간 변경이 쉬워지고 의미가 명확해짐 |
| 큰 `analyze_ktx()` 함수 분할 | **반영** | 로드/월집계/추세/역집계/Summary 생성을 각각 테스트하기 쉬움 |
| 전월 대비 증감률 계산 함수화 | **반영** | 동일한 0 나눗셈 방어 로직 재사용 가능 |
| 구조화 Summary 유지 | **유지** | FastAPI 응답과 System Prompt Context에 적합 |

> Code Review는 전반적으로 높은 완성도로 평가했고, 개선점도 오류 수정이라기보다 **유지보수성·가독성 향상을 위한 리팩터링**에 가깝습니다.



## seed_firestore.py Code Review 2 검토

첨부한 `코드리뷰어2.jpg`를 검토했습니다.

### 확인된 장점

- 입력 CSV에 대한 방어적 검증이 충분함
- 날짜 기반 Document ID + `set()`으로 멱등성 확보
- 168건을 Batch Write로 처리하는 구조가 현재 데이터 규모에 적합
- 업로드 후 별도 검증 단계를 둔 점이 좋음
- Firebase Admin SDK 중복 초기화를 피하는 방향이 적절함

### 개선 제안과 결정

| 제안 | 결정 | 이유 |
|---|---|---|
| Firestore Batch를 400건 단위로 분할 | **반영** | 향후 500건 이상으로 데이터가 늘어날 가능성에 대비 |
| 전체 컬렉션 count 비교 대신 Seed 대상 ID 검증 | **반영** | CRUD로 다른 문서가 추가되어도 Seed 검증이 실패하지 않게 함 |
| 업로드 후 필드값까지 검증 | **추가 반영** | 문서 존재뿐 아니라 `date/value/memo` 일치 여부까지 확인 |
| `get_firestore_client()` 반환 타입 명시 | **반영** | IDE/가독성 개선 |
| DB 인자 타입 힌트 추가 | **반영** | 함수 계약을 명확하게 함 |
| `MIN_REQUIRED_ROWS` 의미 설명 | **반영** | 과제 최소 100건 요구와 코드의 연결을 명확하게 함 |

> Code Review 2의 개선점은 현재 168건에서 발생한 오류를 수정하는 성격보다는,
> **향후 데이터 증가와 CRUD 이후 상태까지 고려한 안정성·정확성·유지보수성 강화**에 가깝습니다.

---

## seed_firestore.py 추가 Code Review (`코드리뷰어.txt`)

추가 리뷰에서는 현재 코드를 매우 훌륭하다고 평가하고, 운영 환경에서 고려할 선택 제언 2개를 제시했습니다.

| 제언 | 결정 | 이유 |
|---|---|---|
| `verify_upload()` 성공 로그에 검증 시간 범위 추가 | **현재 유지** | `load_seed_data()` 로그에서 이미 `first=2010-01-01`, `last=2023-12-01`을 출력하므로 현재 과제에서는 충분함 |
| 대용량 시 `verify_upload()`를 별도 스크립트로 분리 | **미반영** | 현재 168건 규모에서는 업로드 직후 검증까지 한 번에 수행하는 편이 더 단순하고 안전함 |

> 두 제언 모두 좋은 운영 최적화 아이디어지만, 현재 과제 규모에서는 **코드를 더 복잡하게 만들 정도의 실익이 없으므로 현 상태를 유지**합니다.

---

## KTX 데이터 선정 결정 — 1차

### 결론

첫 번째로 받을 핵심 원본 데이터는 **한국철도공사 「KTX 상하행 역별 승하차」 CSV**로 정합니다.

- 제공기관: 한국철도공사
- 공개 형식: CSV
- 공개 범위: 2010년~2023년 KTX 정차역
- 주요 컬럼: `운행년월`, `정차역`, `하행_승차인원수`, `하행_하차인원수`, `상행_승차인원수`, `상행_하차인원수`
- 전체 행: 약 6,953행
- 비용: 무료
- 과제 최소 기준인 100개 데이터 포인트를 충분히 충족
- 월별·역별·방향별 KTX 수요 변화와 장기 추세 분석에 적합

공식 페이지:

```text
https://www.data.go.kr/data/15108119/fileData.do
```

다운로드한 원본은 수정하지 않고 아래처럼 저장하는 것을 권장합니다.

```text
data/raw/korail_ktx_station_monthly_2010_2023.csv
```

> **주의:** 실제 다운로드 파일명이 다르더라도 괜찮습니다. 프로젝트 안에서는 위와 같이 영문 파일명으로 복사/이름 변경하고, 원본 출처명은 README에 기록합니다.

### 왜 이 데이터를 1순위로 선택하는가?

1. KTX에 직접 관련된 공식 데이터입니다.
2. 6천 행 이상이라 과제의 최소 100개 기준을 넉넉하게 충족합니다.
3. `운행년월`이 있어 시계열 분석이 가능합니다.
4. 역별·상행/하행별 차이를 비교할 수 있습니다.
5. API Key 없이 CSV 파일을 먼저 내려받아 전처리 연습을 시작할 수 있습니다.

### 이 데이터만으로 할 수 있는 분석

- 월별 KTX 이용 추세
- 역별 수요 규모 비교
- 상행/하행 수요 차이
- 연도별 증가·감소 추세
- 특정 역의 계절적 수요 변화
- 최근 기간 대비 과거 평균 변화율
- 역·방향 기준 수요 집중도

### 이 데이터만으로는 아직 할 수 없는 것

이 데이터는 **월별 집계 자료**이므로 아래를 직접 증명할 수 없습니다.

- 금요일 저녁의 실제 승차 수요
- 일요일 저녁의 실제 승차 수요
- 특정 열차의 실시간 잔여석
- 예매 시작 후 몇 시간 만에 매진되는지
- 특정 날짜·시간의 정확한 매진 확률

따라서 1차 버전에서는 **월별·역별·방향별 수요 분석을 핵심 근거**로 사용하고, 금요일/일요일·시간대 관련 기능은 추가 데이터가 확보된 뒤 강화합니다.

---

### 함께 받아 둘 2순위 데이터

**한국철도공사 「운행날짜 객실별 이용인원」 CSV**

공식 페이지:

```text
https://www.data.go.kr/data/15110013/fileData.do
```

공공데이터포털 설명상 여객 승하차 흐름을 분석하기 위한 자료이며 약 9,379행입니다.

다만 현재 공개 메타데이터의 실제 컬럼에는 `운행연월`, `정차역이력`, `역무열차종별`, `상하행구분`, `승차인원수`, `하차인원수`, `통과인원수`가 표시되어 있어, 이름만 보고 **일자·열차번호·시간대 데이터가 들어 있다고 가정하지 않습니다.**

다운로드 후 실제 CSV를 열어 컬럼과 값 범위를 확인한 뒤 사용할지 최종 결정합니다.

권장 저장명:

```text
data/raw/korail_train_passenger_2019.csv
```

---

### 실시간/현재 운행정보에 사용할 후보 — 나중 단계

#### 국토교통부 TAGO 열차정보 API

KTX를 포함한 열차의 출발역·도착역 기준 운행시간표, 출발시간, 도착시간 등을 조회할 수 있습니다.

```text
https://www.data.go.kr/data/15098552/openapi.do
```

이 API는 **현재 이동 선택지와 시간표를 보여주는 기능**에는 유용하지만, 과거 이용객 수나 좌석 매진 이력을 제공하는 데이터는 아니므로 핵심 시계열 데이터 대신 보조 기능으로 사용합니다.

#### 국토교통부 TAGO 고속버스정보 API

```text
https://www.data.go.kr/data/15098522/openapi.do
```

출발/도착 터미널, 출발시간, 도착시간, 버스 등급, 요금 정보를 조회할 수 있어 KTX 대체수단 비교 기능에 적합합니다.

#### 국토교통부 TAGO 시외버스정보 API

```text
https://www.data.go.kr/data/15098541/openapi.do
```

현재 공개 안내상 당일 배차정보 중심이므로, 과거 시계열 학습데이터보다 **당일 대체 이동수단 조회 기능**으로 사용하는 편이 적합합니다.

---

### 지금은 받지 않아도 되는 자료

다음 자료는 참고자료로는 쓸 수 있지만 현재 핵심 데이터로는 우선순위가 낮습니다.

- `한국철도공사_연도별 수송실적`: 연간 단위이며 KTX 외 열차종도 포함
- `한국철도공사_역별 승하차 현황`: 간선여객 전체의 연간 누계로 KTX만 분리된 핵심 자료가 아님
- `기관사용 내비게이션_일별 열차 정보 통계`: 현재 공개 파일은 행 수가 적고 이용객 수가 아니라 열차 운행 횟수 중심

---

### 실제 다운로드 데이터 검사 결과

#### 1) 핵심 데이터 — `korail_ktx_station_monthly_2010_2023.csv`

업로드한 원본 CSV를 실제로 확인한 결과입니다.

| 항목 | 확인 결과 |
|---|---|
| 행 × 열 | **6,953행 × 6열** |
| 기간 | **2010-01 ~ 2023-12** |
| 고유 월 | **168개월** |
| 고유 정차역명 | **73개** |
| 결측치 | **0건** |
| 완전 중복 행 | **0건** |
| 인원 컬럼 자료형 | 정수형으로 정상 인식 |
| 과제 100개 기준 | **충족** |

실제 컬럼:

```text
운행년월
정차역
하행_승차인원수
하행_하차인원수
상행_승차인원수
상행_하차인원수
```

주요 역으로 `서울`, `광명`, `천안아산`, `대전`, `동대구`, `부산` 등이 실제 포함되어 있습니다.

**판정:** 이 파일을 프로젝트의 **핵심 장기 시계열 데이터**로 사용합니다.

---

#### 2) 보조 후보 — `korail_train_passenger_2019.csv`

업로드한 두 번째 CSV도 실제로 확인했습니다.

| 항목 | 확인 결과 |
|---|---|
| 행 × 열 | **9,379행 × 7열** |
| 기간 | **2019-04 ~ 2019-12** |
| 고유 월 | **9개월** |
| `정차역이력` 고유 코드 | **272개** |
| `역무열차종별` 고유 코드 | **9개** |
| 상하행 | `D`, `U` |
| 결측치 | **0건** |
| 완전 중복 행 | **0건** |

실제 컬럼:

```text
운행연월
정차역이력
역무열차종별
상하행구분
승차인원수
하차인원수
통과인원수
```

파일명에는 `운행날짜`가 들어 있지만, 실제 CSV의 시간 필드는 **`운행연월`(월 단위)** 입니다. 또한 역명이 아니라 `정차역이력` 코드, 열차명 대신 `역무열차종별` 코드가 들어 있으며, 현재 파일만으로는 각 코드가 어떤 역/열차종을 의미하는지 안전하게 해석할 수 없습니다.

**판정:** 현재 단계에서는 이 파일을 핵심 분석 데이터로 합치지 않고 **보조·참고 원본으로 보관**합니다. 코드 정의표를 확보하기 전에는 KTX만 필터링하거나 금요일/일요일·시간대 분석에 사용했다고 쓰지 않습니다.

---

### 추가로 받을 가치가 있는 보조 데이터 — 시간대 패턴

이번 서비스의 실제 문제의식인 **저녁 시간대와 일요일 혼잡**을 보완하기 위해 다음 공개자료를 보조 데이터로 사용하는 것을 권장합니다.

**한국교통안전공단 「지역 간 대중교통 시간대별 철도 이용인원_20251231」**

```text
https://www.data.go.kr/data/15119714/fileData.do
```

업로드한 실제 CSV를 확인했습니다.

| 항목 | 확인 결과 |
|---|---|
| 행 × 열 | **24행 × 4열** |
| 시간대 | **00:00~00:59 ~ 23:00~23:59** |
| 컬럼 | `구분1`, `평일평균`, `토요일`, `일요일` |
| 결측치 | **0건** |
| 완전 중복 행 | **0건** |
| 평일 최대 시간대 | **18:00~18:59 / 30,029명** |
| 토요일 최대 시간대 | **10:00~10:59 / 44,369명** |
| 일요일 최대 시간대 | **15:00~15:59 / 43,525명** |

이 자료는 평일 평균 / 토요일 / 일요일 이용인원을 직접 비교할 수 있어 **저녁 및 주말 철도 이용 패턴을 보완하는 보조 데이터**로 사용합니다.

단, 일반철도에 고속철도가 포함된 자료이지 **KTX 전용 데이터는 아니므로** `KTX 시간대별 이용률`로 표현하지 않습니다. 또한 금요일이 별도 컬럼이 아니므로 **금요일 저녁 전용 KTX 수요라고 표현하지 않습니다.**

프로젝트 내부 권장 파일명:

```text
data/raw/kotsa_rail_hourly_weekday_weekend_2025.csv
```

> 원본 기관명을 README에 기록하므로 프로젝트 내부 파일명은 영문 소문자 + 언더스코어로 단순화합니다.

---

### 현재 데이터 역할 정리

```text
[핵심]
KTX 상하행 역별 승하차 2010~2023
→ 월별 / 역별 / 상하행 장기 수요

[보조 후보]
운행날짜 객실별 이용인원 2019
→ 현재는 코드 정의 부족으로 참고 보관

[보조 확정]
지역 간 대중교통 시간대별 철도 이용인원 2025
→ 평일 / 토요일 / 일요일 24시간대 철도 이용 패턴
→ KTX 전용 수치로 해석하지 않고 보조지표로만 사용

[나중 단계]
TAGO 열차정보 API
→ 현재 운행시간표 표시

[나중 단계]
TAGO 고속버스 / 시외버스 API
→ KTX 이용이 어려울 때 대체수단 정보 표시
```

> **중요:** TAGO 현재 열차시간표는 지금 구현할 핵심 시계열 분석 데이터가 아니라, **서비스 후반에 현재 이동 선택지를 보여주기 위한 참고/보조 기능**입니다.

---

### 다음 전처리 방향

핵심 CSV는 `상행/하행`을 긴 형식(Long Format)으로 변환하는 것을 권장합니다.

예상 가공 컬럼:

```text
date
station
direction
boardings
alightings
value
memo
```

권장 의미:

- `date`: `운행년월`을 `YYYY-MM-01` 형태로 변환
- `station`: 정차역
- `direction`: `up` 또는 `down`
- `boardings`: 해당 역·방향 승차인원
- `alightings`: 해당 역·방향 하차인원
- `value`: **승차인원(boardings)** 을 과제의 대표 시계열 값으로 사용
- `memo`: `정차역 / 상행·하행 / 월별 KTX 승차수요`

`value`를 승차인원으로 잡는 이유는 이번 서비스가 **출발 시점의 예매 수요를 이해하는 것**이 핵심이기 때문입니다. 하차인원은 별도 분석 필드로 유지합니다.

가공 결과 권장 파일:

```text
data/processed/ktx_demand.csv
```

> 예매난 위험도 점수는 아직 만들지 않습니다. 먼저 실제 승차수요 시계열을 안정적으로 만든 뒤, 보조 시간대 데이터와 함께 점수 산식을 설계합니다.

---

## 권장 개발 순서

1. **프로젝트 기본 구조 만들기**
   - `backend/`, `frontend/`, `data/raw/`, `data/processed/`, `docs/images/`, `scripts/` 생성
   - `requirements.txt`, `.gitignore`, `.env.example` 생성
2. **KTX 핵심 데이터 확보**
   - 먼저 KTX 데이터만으로 100개 이상 확보
   - 출처, 기간, 행 수, 컬럼을 기록
3. **Python 전처리·분석**
   - 날짜 정리, 결측/중복 확인, 요일·시간대 파생변수 생성
   - 기간/개수/평균/최대/최소/최근 추세 계산
4. **예매난 위험도 설계**
   - 실제 공개 데이터가 뒷받침하는 범위에서 점수 산식 정의
   - 정확한 '매진 확률'로 표현하지 않기
5. **FastAPI**
   - Data CRUD + Summary + Conversation + Chat API
6. **Firestore**
   - `data`, `conversations` 컬렉션 연결
7. **GPT Context Injection**
   - Summary를 System Prompt에 넣어 데이터 기반 답변 생성
8. **Vanilla Frontend**
   - 데이터 요약 / AI 채팅 / 데이터 관리 / 대화 기록
9. **배포**
   - Render Backend → Swagger 확인
   - Vercel Frontend → 실제 API 통신 확인
10. **보너스**
   - 추가 통계 → 그래프 → CSV/JSON → 다크모드
   - 여유가 있으면 Function Calling → MCP/GPT Actions
11. **최종 검증**
   - README와 실제 코드/URL/스크린샷 일치 여부 확인

---

# 1. 프로젝트 소개

## 1-1. 서비스명

**KTX 예매난 위험도 분석 및 대체 이동수단 선택 AI 비서**

> **힌트:** 서비스가 무엇을 분석하고 사용자가 무엇을 결정하도록 돕는지 한눈에 알 수 있는 이름을 적습니다.

## 1-2. 한 줄 소개

KTX 이용 데이터를 분석해 특정 날짜·요일·시간대의 **수요 집중 및 예매난 위험도를 이해하기 쉽게 설명하고**, KTX 이용이 어려울 것으로 예상될 때 고속·시외버스 및 자가용 등 대체 이동수단을 함께 검토할 수 있도록 돕는 데이터 기반 AI 비서입니다.

> **힌트:** “무슨 데이터를 분석해, 누구의 어떤 문제를 해결하는 서비스인지” 한 문장으로 적습니다.

## 1-3. 주제 선정 이유

장거리 이동 시 KTX는 빠르고 편리하지만, 금요일 저녁·일요일 저녁·연휴 전후처럼 이용객이 몰리는 시기에는 좌석을 구하기 어려운 경우가 있습니다.  
또한 동대구역처럼 철도역과 고속·시외버스 터미널이 가까운 복합환승지역에서는 KTX를 이용하지 못하더라도 다른 교통수단으로 비교적 쉽게 전환할 수 있지만, 많은 지역에서는 KTX역과 버스터미널이 떨어져 있어 **KTX를 예매하지 않고 역에 갔다가 열차를 타지 못하면 버스까지 놓칠 수 있는 문제**가 있습니다.

저 역시 서울행 KTX 첫차를 입석으로 이용하거나, 원하는 시간대의 열차를 이용하지 못해 지하철로 다른 지역까지 이동한 뒤 고속·시외버스로 갈아탄 경험이 있습니다. 이러한 경험을 통해 단순히 “KTX가 가장 빠른가?”만 보는 것이 아니라 **요일·시간대·연휴 여부·구간별 수요와 대체 교통수단의 이용 가능성까지 함께 확인할 필요가 있다**고 생각했습니다.

따라서 본 프로젝트에서는 KTX 관련 시계열 데이터를 분석하여 특정 시기의 **수요 집중도와 예매난 위험도를 파악**하고, 사용자가 “KTX를 이용할지, 버스를 이용할지, 자가용을 이용할지” 결정하는 데 참고할 수 있는 AI 비서를 구현하고자 합니다.

> **힌트:** 본인이 실제로 겪은 불편 → 왜 단순 KTX 통계만으로 부족한지 → 이 서비스를 만들려는 이유 순서로 적으면 자연스럽습니다.

## 1-4. 해결하려는 문제

- 특정 요일·시간대에 KTX 수요가 집중되는지 미리 파악하기 어렵다.
- KTX를 예매하지 못한 뒤 버스나 자가용으로 변경하려면 이동시간과 환승거리 때문에 대응이 늦을 수 있다.
- 단순 평균 이용률은 실제 특정 시간대의 예매난을 충분히 설명하지 못한다.
- 여러 교통수단 정보를 사용자가 직접 따로 찾아 비교해야 한다.
- 공개 데이터만으로 “정확한 매진 확률”을 단정하기 어렵기 때문에, 근거가 있는 **예매난 위험도/수요 집중도** 형태의 설명이 필요하다.

> **힌트:** 사용자가 현재 겪는 불편을 3~5개 정도 구체적으로 적습니다.

## 1-5. 서비스 목표

1. KTX 관련 시계열 데이터를 최소 100개 이상 확보하고 분석한다.
2. 기간, 데이터 개수, 평균, 최대, 최소, 최근 추세 등 요약 정보를 제공한다.
3. 분석 데이터를 Firestore에 저장하고 CRUD로 관리한다.
4. 데이터 요약을 시스템 프롬프트에 주입하여 AI가 사용자의 실제 데이터를 기반으로 답변하도록 한다.
5. 이전 대화를 저장하고 다시 불러올 수 있도록 한다.
6. Render와 Vercel에 실제 배포하여 평가자가 웹에서 확인할 수 있도록 한다.
7. **[권장]** KTX 예매난 위험도와 함께 버스·자가용 관련 정보를 비교해 이동수단 결정에 참고할 수 있도록 한다.

> **힌트:** 과제 필수 기능을 먼저 적고, 그다음 이번 KTX 프로젝트만의 목표를 추가합니다.

---

# 2. 핵심 기능

## 2-1. 데이터 기반 AI 채팅

사용자가 자연어로 질문하면 Firestore에 저장된 KTX 관련 데이터의 요약 정보를 시스템 프롬프트에 넣고 GPT API를 호출하여 데이터 기반 답변을 제공합니다.

예상 질문 예시:

- “이번 금요일 저녁 KTX 수요가 높은 편이야?”
- “금요일 저녁과 토요일 아침 중 어느 쪽이 덜 붐벼?”
- “지난해 같은 시기의 수요는 평소보다 높았어?”
- “KTX 이용이 어려울 것 같으면 다른 이동수단도 알려줘.”
- “일요일 저녁 서울행은 평소보다 수요가 높은 편이야?”

**[사용자 작성 필요] 실제 구현 후 대표 질문 2~3개와 실제 AI 답변을 넣으세요.**

```text
Q1. [실제 질문]
A1. [실제 AI 답변]

Q2. [실제 질문]
A2. [실제 AI 답변]
```

> **힌트:** 제출 스크린샷에서 그대로 확인할 수 있는 실제 질문·답변을 넣습니다.

## 2-2. 데이터 관리(CRUD)

과제 요구 형식인 `(date, value, memo)`를 기준으로 데이터를 추가·조회·수정·삭제합니다.

예시:

```json
{
  "date": "2026-10-02",
  "value": 82,
  "memo": "서울→동대구 / 금요일 저녁 / 연휴 전"
}
```

- `date`: 기준 날짜
- `value`: 분석 값 또는 예매난 위험도/수요 지표
- `memo`: 노선, 요일, 시간대, 특수일 등 부가 설명

**[사용자 작성 필요] 실제 최종 데이터 스키마가 위 구조와 다르면 아래에 정확한 필드를 적으세요.**

```text
최종 데이터 필드:
- date:
- value:
- memo:
- 추가 필드:
```

> **힌트:** Firestore `data` 컬렉션에 실제 저장되는 필드명을 그대로 적습니다.

## 2-3. 대화 기록 저장 및 불러오기

AI와의 대화를 Firestore `conversations` 컬렉션에 저장하고, 이전 대화 목록을 조회한 뒤 특정 대화를 다시 불러올 수 있도록 구현합니다.

**[사용자 작성 필요] 아래 A/B 중 실제 구현 방식을 하나 선택해 남기세요.**

- [ ] **A 방식:** `GET /api/conversations/{id}`로 특정 대화의 전체 `messages` 조회
- [ ] **B 방식:** `GET /api/conversations` 응답에 `messages`를 포함하여 반환

> **힌트:** 실제 코드에서 이전 대화를 불러오는 방식과 일치하는 항목만 체크합니다.

## 2-4. 데이터 요약

현재 저장된 데이터에서 다음 정보를 계산하여 화면과 AI 컨텍스트에 사용합니다.

### 과제 필수 요약
- 분석 기간
- 총 데이터 개수
- 평균
- 최대
- 최소
- 최근 추세: 증가 / 감소 / 유지

### KTX 프로젝트 권장 요약

**현재 핵심 CSV로 바로 구현 가능한 항목**
- 역별 월평균 승차수요
- 상행/하행 평균 차이
- 최근 월 또는 최근 연도 대비 변화율
- 역별 장기 추세
- 월별 수요 집중도

**추가 보조데이터 확보 후 구현할 항목**
- 평일/토요일/일요일 시간대 패턴
- 저녁 시간대 수요 집중도
- 연휴/특수일과 일반일 비교
- 예매난 위험도 또는 수요 집중도 결합점수

> 현재 핵심 CSV는 월 단위이므로 `금요일 저녁 KTX 수요`를 직접 계산했다고 표현하지 않습니다.

**[사용자 작성 필요] 실제 구현된 항목만 남기고 계산식을 적으세요.**

```text
예매난 위험도 산식:
[여기에 실제 계산식 또는 가중치 작성]

예:
- 요일 효과:
- 시간대 효과:
- 연휴 효과:
- 과거 이용량:
- 노선 수요:
- 최종 점수 계산:
```

> **힌트:** “왜 82점인지” 설명할 수 있도록 실제 점수 계산 근거를 적습니다. 아직 결정하지 않았다면 구현 후 확정하세요.

### 현재 구현 완료된 기본 분석 Summary

```text
기간: 2010-01-01 ~ 2023-12-01
가공 레코드: 13,906
정차역: 73개
value: 역·방향별 월 승차인원

평균: 57,832.72
최대: 1,484,629
최소: 0

2023-12 총승차인원: 6,839,626
2023-11 총승차인원: 6,642,320
전월 대비: +2.97%

최근 12개월 월평균: 6,342,093.08
직전 12개월 월평균: 5,318,481.33
변화율: +19.25%
최근 추세: 증가
```

최근 추세 판정:

```text
변화율 >= +3% → 증가
변화율 <= -3% → 감소
그 사이          → 유지
```

> 이 Summary는 `analysis_summary.json`의 실제 실행 결과를 기준으로 작성했습니다.


---

# 3. 데이터 선정 및 분석

## 3-1. 사용 데이터

### [AI 작성 완료] 현재 데이터 선정 상태

- **핵심 확정:** 한국철도공사 `KTX 상하행 역별 승하차` CSV — 실제 파일 검사 완료
- **보조 보관:** 한국철도공사 `운행날짜 객실별 이용인원` CSV — 실제 파일 검사 완료, 코드 정의 부족으로 현재 핵심 분석에서는 제외
- **보조 확정:** 한국교통안전공단 `지역 간 대중교통 시간대별 철도 이용인원_20251231` — 실제 파일 검사 완료, 평일/토요일/일요일 24시간대 철도 이용 패턴
- **나중 참고:** 국토교통부 TAGO 열차정보 API — 현재 운행시간표
- **나중 대체수단:** 국토교통부 TAGO 고속버스 API
- **나중 대체수단:** 국토교통부 TAGO 시외버스 API
- **향후 보조:** 한국도로공사 시간대별 교통량 및 도시간 통행시간

**[사용자 작성 필요] 최종 프로젝트에서 실제 사용한 데이터만 아래 표에 남기세요.**

| 구분 | 실제 데이터/API명 | 제공기관 | 기간 | 데이터 개수 | 용도 |
|---|---|---|---|---:|---|
| KTX | KTX 상하행 역별 승하차 | 한국철도공사 | 2010-01 ~ 2023-12 | 6,953행 | 핵심 월별·역별·방향별 시계열 분석 |
| 철도 시간대 패턴 | 지역 간 대중교통 시간대별 철도 이용인원 | 한국교통안전공단 | 2025 공개자료 | 24행 | 평일/토요일/일요일 시간대 패턴 보조 |
| 고속버스 | [작성/미사용] | [작성] | [작성] | [작성] | 대체 교통수단 |
| 시외버스 | [작성/미사용] | [작성] | [작성] | [작성] | 대체 교통수단 |
| 자동차 | [작성/미사용] | [작성] | [작성] | [작성] | 도로 혼잡/소요시간 |

> **힌트:** “후보”가 아니라 실제 코드·CSV에 사용한 데이터만 적습니다.

## 3-2. 분석 범위

**[사용자 작성 필요]**

```text
분석 기간: 2010-01 ~ 2023-12
원본 데이터 포인트: 6,953행
고유 정차역명: 73개
핵심 시간 단위: 월
핵심 공간 단위: 역 + 상행/하행
노선/OD(출발역→도착역) 단위: 현재 핵심 CSV만으로는 직접 제공되지 않음
요일/시간대: 보조 데이터로 별도 보강 예정
특수일 구분: 현재 핵심 CSV에는 없음
```

> **힌트:** CSV 또는 Firestore의 실제 데이터 범위와 개수를 확인해 적습니다.

## 3-3. 전처리

**[사용자 작성 필요] 실제 수행한 것만 체크하고 설명을 추가하세요.**

- [x] 날짜 형식 통일 (`YYYY-MM` → `YYYY-MM-01`)
- [x] 결측치 확인 (핵심 원본 0건)
- [x] 완전 중복 여부 확인 (핵심 원본 0건, 제거 불필요)
- [ ] 역/노선명 표준화
- [x] 상행/하행을 `up` / `down` Long Format으로 변환
- [ ] 요일 파생변수 생성
- [ ] 시간대 파생변수 생성
- [ ] 공휴일/연휴 여부 생성
- [ ] 정책 변화 구간 변수 생성
- [ ] 이상치 확인
- [x] 기타: 인원 컬럼 숫자형 검증, 필수 컬럼 검증, CSV 인코딩 자동 시도

```text
전처리 설명:
1. 공공데이터 CSV를 cp949, utf-8-sig, euc-kr, utf-8 순서로 읽기 시도
2. 필수 컬럼 존재 여부 검증
3. 운행년월을 YYYY-MM-01 날짜 형식으로 통일
4. 승·하차 인원 컬럼을 숫자형으로 검증
5. 상행/하행 Wide 데이터를 Long Format으로 변환
6. value는 승차인원(boardings)으로 지정
7. 과제 CRUD 구조와 AI 설명에 사용할 memo 생성
8. 시간대 보조자료는 24시간대 × 3요일유형을 72행 Long Format으로 변환
9. UTF-8-SIG CSV로 data/processed에 저장
```

> **힌트:** Notebook/Python 전처리 코드에서 실제 수행한 작업을 순서대로 적습니다.

## 3-4. 데이터 해석상의 한계

본 프로젝트에서 사용하는 공개 데이터만으로는 특정 열차가 **언제 정확히 매진되는지**, 또는 특정 시각에 **몇 % 확률로 매진되는지**를 직접 알 수 없는 경우가 있습니다.

따라서 서비스에서는 가능한 한 다음 표현을 사용합니다.

- ❌ “이 열차는 93% 확률로 매진됩니다.”
- ✅ “과거 이용 패턴을 기준으로 수요 집중도가 높습니다.”
- ✅ “예매난 위험도가 높은 구간입니다.”
- ✅ “조기 예매를 고려할 수 있는 시기입니다.”

**[권장]** 데이터 수집 시점 전후로 좌석 공급 체계나 운영정책이 크게 변경된 경우에는 `policy_change`, `integration_period` 같은 변수를 두어 이전·이후 데이터를 단순 비교하지 않도록 합니다.

> **힌트:** 모델이 실제 데이터보다 강하게 단정하지 않도록 데이터의 한계를 README에 명시합니다.

---

# 4. 시스템 구조

## 4-1. 전체 흐름

```text
공공데이터 / CSV / 외부 API
        ↓
Python 전처리 및 시계열 분석
        ↓
Firebase Firestore
 ├─ data
 └─ conversations
        ↓
FastAPI
 ├─ Data CRUD
 ├─ Summary
 ├─ Conversation API
 └─ Chat API
        ↓
데이터 Summary
        ↓
System Prompt Context Injection
        ↓
OpenAI GPT API
        ↓
AI 답변 + 대화 자동 저장
        ↓
HTML / CSS / JavaScript Frontend
        ↓
Vercel
```

> **힌트:** 평가자가 “데이터가 어디에서 와서 AI 답변까지 어떻게 가는지” 한눈에 이해하도록 적습니다.

## 4-2. AI 컨텍스트 주입 원리

일반적인 GPT는 프로젝트의 Firestore 데이터를 자동으로 알지 못합니다.  
따라서 `/api/data/summary`에서 현재 데이터를 요약한 뒤 해당 결과를 시스템 프롬프트에 삽입하여 GPT가 실제 분석 데이터를 바탕으로 답하도록 합니다.

예시:

```text
당신은 KTX 수요 분석 및 이동수단 선택을 돕는 데이터 분석 AI 비서입니다.

[현재 데이터 요약]
- 분석 기간: {period}
- 총 레코드: {count}
- 평균: {average}
- 최대: {max}
- 최소: {min}
- 최근 추세: {trend}
- 선택 역: {station}
- 방향: {direction}
- 최근 변화율: {change_rate}

위 데이터에 근거해 답변하세요.
현재 핵심 데이터는 월별·역별·상하행 집계 데이터입니다.
데이터로 확인할 수 없는 금요일 저녁 전용 수요, 실제 잔여 좌석, 매진 확률은 단정하지 마세요.
```

**[사용자 작성 필요] 구현 후 실제 시스템 프롬프트의 핵심 규칙과 변수명을 맞춰 수정하세요.**

> **힌트:** API Key나 내부 비밀정보는 빼고, AI에게 어떤 데이터와 규칙을 주는지만 보여줍니다.

---

# 5. 기술 스택

| 영역 | 기술 |
|---|---|
| Backend | FastAPI |
| Language | Python 3.10 이상 |
| Validation | Pydantic |
| Database | Firebase Firestore |
| AI | OpenAI GPT API |
| Firebase Console AI 보조 | Gemini in Firebase 사용 안 함 (과제 필수 아님) |
| Frontend | HTML / CSS / JavaScript |
| Backend Deploy | Render |
| Frontend Deploy | Vercel |
| Version Control | Git / GitHub |

**[사용자 작성 필요] 실제 사용 버전 및 추가 라이브러리**

```text
Python:
FastAPI:
Uvicorn:
firebase-admin:
openai:
python-dotenv:
기타:
```

> **힌트:** `requirements.txt` 또는 실제 개발환경에서 확인한 버전을 적습니다.

---

# 6. 개발 환경

## 6-1. 필수 환경

- Python 3.10 이상
- 가상환경 `venv`
- Firebase 프로젝트
- Firebase 서비스 계정
- OpenAI API Key
- Render 계정
- Vercel 계정

### 과제 지정 핵심 패키지

```text
fastapi
uvicorn
firebase-admin
openai
python-dotenv
```

**[사용자 작성 필요] `requirements.txt`에 최종 패키지를 모두 기록하세요.**

> **힌트:** 로컬에서 설치한 패키지와 Render가 설치하는 패키지가 같아야 합니다.

---

# 7. 프로젝트 구조

**[사용자 작성 필요] 구현 완료 후 실제 폴더 구조로 교체하세요.**

```text
ktx-congestion-analysis/
├─ backend/
│  ├─ main.py
│  ├─ routers/
│  │  ├─ data.py
│  │  ├─ conversations.py
│  │  └─ chat.py
│  ├─ services/
│  │  ├─ data_service.py
│  │  ├─ firestore_service.py
│  │  └─ ai_service.py
│  ├─ models/
│  ├─ requirements.txt
│  └─ .env.example
├─ frontend/
│  ├─ index.html
│  ├─ style.css
│  ├─ app.js
│  └─ config.js
├─ data/
│  ├─ raw/
│  └─ processed/
├─ scripts/
│  ├─ collect_data.py
│  └─ preprocess_data.py
├─ docs/
│  └─ images/
├─ README.md
└─ .gitignore
```

> **힌트:** 실제 저장소 구조를 `tree` 또는 VS Code Explorer를 보고 그대로 적습니다.

---

# 8. FastAPI 구성

## 8-1. 앱 초기화

- [ ] FastAPI 앱 초기화
- [ ] Router 분리
- [ ] Service 분리
- [ ] CORS 설정
- [ ] 로컬 실행 확인
- [ ] `/docs` Swagger UI 확인

로컬 실행 예시:

```bash
uvicorn backend.main:app --reload
```

**[사용자 작성 필요] 실제 실행 명령이 다르면 수정하세요.**

> **힌트:** 프로젝트 루트에서 실제로 실행되는 명령을 그대로 적습니다.

## 8-2. Router / Service 분리 기준

**[AI 초안]**

- Router는 HTTP 요청·응답과 상태 코드를 담당합니다.
- Service는 Firestore 조회, 데이터 요약, AI 호출 등 실제 비즈니스 로직을 담당합니다.
- 데이터 모델과 검증 규칙은 Pydantic Model로 분리합니다.

**[사용자 작성 필요] 실제 코드 구조와 다르면 맞게 수정하세요.**

> **힌트:** “왜 파일을 나눴는지” 평가자에게 설명할 수 있는 정도로 적으면 됩니다.

---

# 9. Firestore 설계

## Gemini in Firebase와 Firestore 역할 구분

- **Firestore**: KTX 시계열 데이터와 AI 대화 기록을 저장하는 데이터베이스
- **OpenAI GPT API**: 데이터 Summary를 바탕으로 사용자 질문에 답변하는 AI
- **Gemini in Firebase**: Firebase Console에서 개발을 돕는 선택적 AI 보조 기능
- 이번 프로젝트에서는 **Gemini in Firebase를 애플리케이션 AI로 연결하지 않음**



## 9-1. 컬렉션

### `data`

과제 필수 시계열 데이터로 `monthly_summary.csv`의 전국 KTX 월 총승차인원 **168건**을 저장합니다.

```json
{
  "date": "2010-01-01",
  "value": 3219534,
  "memo": "전국 KTX 월 총승차인원"
}
```

### `conversations`

AI 대화 기록을 저장합니다.

```json
{
  "title": "[대화 제목]",
  "messages": [
    {
      "role": "user",
      "content": "[질문]"
    },
    {
      "role": "assistant",
      "content": "[답변]"
    }
  ]
}
```

**[사용자 작성 필요] 실제 Firestore 문서 구조와 필드명을 구현 후 맞춰 쓰세요.**

> **힌트:** Firebase Console에서 실제 Document를 확인하면서 작성합니다.

---

# 10. API 명세

## 10-1. 데이터 API — 필수 5개

| Method | Endpoint | 기능 | 구현 |
|---|---|---|---|
| POST | `/api/data` | 새 데이터 추가 | [ ] |
| GET | `/api/data` | 데이터 목록 조회 | [ ] |
| PUT | `/api/data/{id}` | 데이터 수정 | [ ] |
| DELETE | `/api/data/{id}` | 데이터 삭제 | [ ] |
| GET | `/api/data/summary` | 데이터 요약 | [ ] |

> **힌트:** Swagger에서 실제 성공한 API만 체크합니다.

## 10-2. 대화 기록 API

| Method | Endpoint | 기능 | 구현 |
|---|---|---|---|
| POST | `/api/conversations` | 대화 저장 | [ ] |
| GET | `/api/conversations` | 대화 목록 조회 | [ ] |
| DELETE | `/api/conversations/{id}` | 대화 삭제 | [ ] |
| GET | `/api/conversations/{id}` | 특정 대화 전체 메시지 조회(A 방식) | [ ] |

**[사용자 작성 필요] B 방식을 사용했다면 아래에 응답 구조를 적고 A 방식 행은 삭제하세요.**

> **힌트:** “이전 대화 불러오기”가 실제 프론트에서 동작하도록 만든 API를 정확히 기록합니다.

## 10-3. AI Chat API

| Method | Endpoint | 기능 |
|---|---|---|
| POST | `/api/chat` | 데이터 요약 기반 AI 대화 |

동작 흐름:

```text
사용자 질문
→ /api/data/summary 또는 내부 Summary 함수 조회
→ Summary를 System Prompt에 주입
→ GPT API 호출
→ AI 답변 반환
→ conversations 컬렉션에 자동 저장
```

> **힌트:** 실제 코드에서 Summary를 어디서 만들고, GPT를 어떻게 호출하고, 대화를 언제 저장하는지 적습니다.

---

# 11. Pydantic 입력값 검증

과제에서는 요청 데이터 검증을 적용하고 그 이유를 설명할 수 있어야 합니다.

**[권장 검증안]**

### Chat
- 빈 문자열 거부
- 최대 길이 제한
- 제어문자 정리 또는 거부

### Data
- `date`: `YYYY-MM-DD` 또는 실제 ISO 날짜 형식 검증
- `value`: 숫자형 검증 및 허용 범위 설정
- `memo`: 최대 길이 설정

### Conversation ID
- 허용 문자 또는 Firestore ID 형식 검증

**[사용자 작성 필요] 실제 적용한 Pydantic 규칙을 적으세요.**

```text
ChatRequest:
DataCreate:
DataUpdate:
Conversation:
기타:
```

> **힌트:** 잘못된 입력을 Swagger에서 한 번씩 테스트하고 README에 규칙을 기록하면 좋습니다.

---

# 12. 오류 처리 및 사용자 안내

과제는 최소한의 예외 처리를 요구합니다.

**[권장] 다음 오류를 구분합니다.**

| 상황 | 사용자 안내 예시 | 개발자 로그 |
|---|---|---|
| 빈 입력 | 질문을 입력해 주세요. | validation error |
| 잘못된 데이터 | 입력 형식을 확인해 주세요. | field/detail 기록 |
| AI API 오류 | AI 응답을 가져오지 못했습니다. 잠시 후 다시 시도해 주세요. | provider error |
| Timeout | 응답 시간이 초과되었습니다. 다시 시도해 주세요. | timeout 로그 |
| Firestore 오류 | 데이터를 불러오지 못했습니다. | DB exception |
| Render Cold Start | 무료 서버가 깨어나는 중입니다. 잠시 기다려 주세요. | 필요 시 기록 |

**[사용자 작성 필요] 실제 UI 문구와 Exception 처리 내용을 맞춰 수정하세요.**

> **힌트:** 사용자에게는 쉬운 문구, 개발 로그에는 원인을 남기는 방식이 좋습니다.

---

# 13. CORS

Render Backend와 Vercel Frontend가 서로 통신할 수 있도록 CORS를 설정합니다.

환경변수 예:

```text
ALLOWED_ORIGINS=https://[내-Vercel-도메인]
```

**[사용자 작성 필요] 최종 Vercel 도메인을 배포 후 설정하세요.**

> **힌트:** 개발 중 `*`를 쓰더라도 최종 배포에서는 가능한 한 실제 Frontend 도메인만 허용하는 것이 좋습니다.

---

# 14. 환경 변수 및 보안

## 14-1. 환경 변수 목록

과제에서 요구하는 최소 환경변수:

```env
OPENAI_API_KEY=
FIREBASE_SERVICE_ACCOUNT_JSON=
API_BASE_URL=
ALLOWED_ORIGINS=
```

구현에 따라 추가:

```env
OPENAI_MODEL=
OPENAI_MAX_TOKENS=
OPENAI_TIMEOUT=
[공공데이터_API_KEY]=
```

> **힌트:** README에는 변수 “이름”만 적고 실제 비밀값은 절대 적지 않습니다.

## 14-2. API Key / 서비스 계정 보안

- `.env`는 Git에 Commit하지 않습니다.
- Firebase 서비스 계정 JSON 원본도 Git에 Commit하지 않습니다.
- 실제 Key는 Render/Vercel 환경변수로 관리합니다.
- `.env.example`에는 변수명만 적습니다.
- 스크린샷에 Key가 노출되지 않도록 확인합니다.
- Key가 노출되었다면 파일 삭제만 하지 말고 즉시 폐기 후 재발급합니다.

`.gitignore` 권장 예:

```gitignore
.env
.env.*
!.env.example
*firebase-adminsdk*.json
serviceAccountKey*.json
secrets/
__pycache__/
*.pyc
venv/
.venv/
```

> **힌트:** GitHub 과거 Commit까지 비밀키가 남지 않았는지 제출 전에 확인합니다.

---

# 15. AI 비용 및 사용량 관리

본 프로젝트는 개인 OpenAI API Key를 사용할 경우 과금이 발생할 수 있습니다.  
개발·테스트 단계에서는 저비용 모델, 요청 횟수 제한, 출력 토큰 제한 등을 적용합니다.

**[현재 계획 초안]**

- 사용자: 과제 수행자 1명 + 평가자 약 1명
- 모델 후보: GPT-5.6 Luna
- 자동충전: OFF 권장
- `max_tokens`: **[사용자 작성 필요: 실제 코드 값]**
- Timeout: **[사용자 작성 필요: 실제 코드 값]**
- Retry: **[사용자 작성 필요: 실제 코드 값]**
- 호출 제한/중복 클릭 방지: **[구현 여부 작성]**

> **힌트:** 실제 코드에 설정한 토큰 제한·Timeout·Retry 값을 그대로 적습니다.

---

# 16. Frontend

과제 제약에 따라 **HTML / CSS / JavaScript만 사용하며 Frontend Framework는 사용하지 않습니다.**

## 16-1. 필수 화면

### ① 데이터 요약
- 분석 기간
- 데이터 개수
- 평균
- 최대
- 최소
- 최근 추세
- **[권장]** 예매난 위험도
- **[추가 보조데이터 확보 후]** 평일/토요일/일요일 시간대 패턴

### ② AI 채팅
- 메시지 입력
- 사용자/AI 메시지 표시
- 로딩 표시
- 오류 표시

### ③ 데이터 관리
- 새 데이터 추가
- 목록 표시
- 수정/삭제 중 최소 1개가 화면에서 실제 동작

### ④ 대화 기록
- 이전 대화 목록
- 특정 대화 불러오기
- 선택한 대화의 메시지 재표시

> **힌트:** 과제의 네 기능이 한 화면이든 탭 구조든 실제 UI에서 확인되도록 만듭니다.

---

# 17. 배포

## 17-1. Backend — Render

- [ ] GitHub에 Backend 코드 Push
- [ ] Render Web Service 생성
- [ ] 환경변수 등록
- [ ] 배포 성공
- [ ] `/docs` Swagger UI 접속 확인
- [ ] Render Cold Start 안내 준비

**[사용자 작성 필요]**

```text
Backend API URL:
https://[작성]

Swagger URL:
https://[작성]/docs
```

> **힌트:** 실제 외부 브라우저에서 접속되는 URL을 적습니다.

## 17-2. Frontend — Vercel

- [ ] Vercel 배포
- [ ] Backend API URL을 환경설정/Config에 연결
- [ ] 실제 Frontend → Render API 통신 확인

**[사용자 작성 필요]**

```text
Frontend URL:
https://[작성]
```

> **힌트:** 평가자가 바로 눌러 사용할 최종 서비스 주소를 적습니다.

---

# 18. 로컬 실행 방법

## 18-1. Backend

```bash
git clone [저장소 URL]
cd ktx-congestion-analysis

python -m venv venv
```

Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

패키지 설치:

```bash
pip install -r backend/requirements.txt
```

환경변수 설정 후 실행:

```bash
uvicorn backend.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

**[사용자 작성 필요] 실제 폴더 위치와 실행 명령에 맞게 수정하세요.**

> **힌트:** 새 PC에서 README만 보고 실행할 수 있을 정도로 순서대로 적습니다.

## 18-2. Frontend

**[사용자 작성 필요] 실제 실행 방법을 적으세요.**

예:

```bash
cd frontend
python -m http.server 5500
```

또는 VS Code Live Server 사용:

```text
frontend/index.html → Open with Live Server
```

> **힌트:** 브라우저에서 HTML 파일을 직접 열 때 CORS 문제가 생긴다면 로컬 서버 방식으로 실행합니다.

---

# 19. 제출 스크린샷

과제 문서에서 README에 다음 3가지 증빙을 요구합니다.

## 19-1. 데이터 요약이 보이는 채팅 화면

**필수 조건**
- 데이터 요약 표시
- 실제 사용자 질문
- 실제 AI 답변
- 가능하면 로딩 완료 화면

```md
![데이터 기반 AI 채팅](docs/images/01_ai_chat.png)
```

**[사용자 작성 필요] 실제 파일명 입력**

> **힌트:** “AI가 데이터 요약을 반영해 답했다”는 것을 한 장에서 볼 수 있게 캡처합니다.

## 19-2. 데이터 관리 화면

**필수 조건**
- 데이터 목록
- CRUD 중 최소 1개 동작이 보이도록 캡처

```md
![데이터 관리](docs/images/02_data_crud.png)
```

**[사용자 작성 필요] 실제 파일명 입력**

> **힌트:** 추가 전/후 또는 수정·삭제 결과가 보이면 평가자가 확인하기 쉽습니다.

## 19-3. 대화 기록 화면

**필수 조건**
- 이전 대화 목록
- 특정 대화 선택
- 불러온 메시지 표시

```md
![대화 불러오기](docs/images/03_conversation_history.png)
```

**[사용자 작성 필요] 실제 파일명 입력**

> **힌트:** 목록을 클릭한 뒤 과거 질문·답변이 다시 표시되는 장면을 캡처합니다.

---

# 20. 테스트 및 검증

**[권장 — 과제 필수 수준을 넘어서는 항목]**

| 테스트 | 예상 결과 | 실제 결과 |
|---|---|---|
| 빈 채팅 입력 | 4xx 또는 사용자 안내 | [작성] |
| 2000자 초과 입력 | Validation Error | [작성] |
| 잘못된 날짜 | Validation Error | [작성] |
| 데이터 추가 | Firestore 저장 + 목록 갱신 | [작성] |
| 데이터 수정 | 값 변경 확인 | [작성] |
| 데이터 삭제 | 목록에서 제거 | [작성] |
| Summary | 기간/개수/통계/추세 반환 | [작성] |
| Chat | Summary 기반 답변 | [작성] |
| 대화 저장 | conversations 저장 | [작성] |
| 대화 불러오기 | 과거 메시지 재표시 | [작성] |
| AI 오류 | 사용자용 오류 문구 | [작성] |
| Timeout | Timeout 안내 | [작성] |
| Render Cold Start | 안내 후 정상 응답 | [작성] |
| Mobile | 레이아웃 정상 | [작성] |

> **힌트:** “내 PC에서는 됨”이 아니라 Swagger와 배포 URL에서 다시 확인합니다.

---

# 21. 보너스 과제 A — Function Calling + 멀티채널 연동

> **선택 과제: 수행한 경우에만 남기세요.**

## 21-1. Function Calling

KTX 프로젝트에서 정의할 수 있는 Tool 예:

```text
get_ktx_demand()
get_data_summary()
get_conversation_history()
get_bus_schedule()
get_road_traffic()
```

예상 흐름:

```text
사용자:
“이번 금요일 서울에서 대구 가려고 하는데 어떻게 갈까?”

        ↓

AI가 질문 분석

        ↓

get_ktx_demand()
        ↓
get_bus_schedule()
        ↓
get_road_traffic()

        ↓

Tool 결과 종합

        ↓

최종 AI 답변
```

**[사용자 작성 필요]**

```text
구현한 Tool:
1.
2.
3.

Tool을 호출하는 판단 기준:
[작성]

Tool 결과 검증 방식:
[작성]
```

> **힌트:** “어떤 질문일 때 어떤 Tool을 왜 호출했는지” 설명할 수 있어야 합니다.

## 21-2. MCP Server 또는 GPT Actions

과제에서는 Function Calling과 같은 기능을 다음 중 **1개 방식**으로 외부 채널/클라이언트에서도 검증하도록 요구합니다.

- [ ] MCP Server
- [ ] GPT Actions

**[사용자 작성 필요]**

```text
선택 방식:
호출한 Tool/API:
검증 방법:
검증 결과:
```

간단 흐름:

```text
외부 Client
→ MCP Server 또는 GPT Actions
→ 내부 기능/API
→ 결과 반환
```

> **힌트:** 실제로 호출 성공한 화면 또는 로그를 증빙으로 남깁니다.

---

# 22. 보너스 과제 B — 인사이트·UX 고도화

> **KTX 프로젝트에는 적극 권장합니다. 비용 증가가 거의 없고 결과가 눈에 잘 보입니다.**

## 22-1. 추가 통계 1개 이상

추천:

- 역별 월평균 승차수요
- 상행/하행 수요 차이
- 전년 동월 대비 변화율
- 최근 12개월 변동성
- **[보조 시간대 데이터 확보 후]** 평일/토요일/일요일 시간대별 수요 차이
- **[추가 데이터 확보 후]** 연휴 vs 일반일 비교
- **[추가 데이터 확보 후]** 예매난 위험도 결합지표

**[사용자 작성 필요] 실제 구현 항목**

```text
추가 지표:
계산식:
해석:
```

> **힌트:** 과제 기본 평균/최대/최소 외에 하나 이상의 새로운 지표를 만듭니다.

## 22-2. 그래프 1개 이상

추천 그래프:

- 요일별 KTX 평균 수요
- 시간대별 수요
- 최근 N주 추세
- 특정 노선 날짜별 수요
- KTX/버스/도로 혼잡 비교

**[사용자 작성 필요]**

```md
![KTX 수요 추세](docs/images/04_chart.png)
```

> **힌트:** 표보다 “언제 수요가 높아지는지”가 바로 보이는 그래프가 좋습니다.

## 22-3. CSV 또는 JSON 다운로드

- [ ] CSV 다운로드
- [ ] JSON 다운로드

**[사용자 작성 필요] 실제 구현한 형식만 체크**

> **힌트:** 현재 필터링된 분석 데이터를 사용자가 파일로 받을 수 있도록 합니다.

## 22-4. 다크모드

- [ ] 다크모드 토글
- [ ] 새로고침 후 선택 상태 유지(localStorage) — **[권장]**

> **힌트:** 필수 기능을 해치지 않도록 마지막 단계에서 추가합니다.

---

# 23. 과제 요구사항 충족 체크리스트

## 개발환경
- [ ] Python 3.10 이상
- [ ] venv 구성
- [ ] fastapi
- [ ] uvicorn
- [ ] firebase-admin
- [ ] openai
- [ ] python-dotenv
- [ ] Firebase 프로젝트/서비스 계정
- [ ] OpenAI API Key
- [ ] Render 계정
- [ ] Vercel 계정

## 데이터
- [ ] 관심 있는 시계열 데이터 선정
- [ ] 데이터 포인트 100개 이상
- [ ] 기간 계산
- [ ] 개수 계산
- [ ] 평균 계산
- [ ] 최대 계산
- [ ] 최소 계산
- [ ] 최근 추세 계산

## FastAPI
- [ ] FastAPI 초기화
- [ ] CORS 설정
- [ ] 로컬 실행 성공
- [ ] `/docs` Swagger 확인

## Firestore
- [ ] Firestore 사용
- [ ] `data` 컬렉션
- [ ] `conversations` 컬렉션
- [ ] 서비스 계정 키 환경변수 관리
- [ ] 코드 하드코딩 없음

## Data API
- [ ] `POST /api/data`
- [ ] `GET /api/data`
- [ ] `PUT /api/data/{id}`
- [ ] `DELETE /api/data/{id}`
- [ ] `GET /api/data/summary`

## Conversation API
- [ ] `POST /api/conversations`
- [ ] `GET /api/conversations`
- [ ] `DELETE /api/conversations/{id}`
- [ ] 특정 대화 messages 불러오기 A 또는 B 구현

## AI Chat
- [ ] `POST /api/chat`
- [ ] 데이터 Summary 조회
- [ ] Summary → System Prompt 주입
- [ ] GPT API 호출
- [ ] conversations 자동 저장

## Backend 배포
- [ ] GitHub Push
- [ ] Render Web Service 배포
- [ ] 배포 URL 접속
- [ ] 배포 URL `/docs` 확인
- [ ] Cold Start 안내/대응

## Frontend
- [ ] HTML
- [ ] CSS
- [ ] JavaScript
- [ ] Frontend Framework 미사용
- [ ] 채팅 입력
- [ ] 대화 표시
- [ ] 로딩 표시
- [ ] 데이터 추가
- [ ] 데이터 목록
- [ ] 수정/삭제 중 최소 1개
- [ ] 이전 대화 목록
- [ ] 대화 불러오기
- [ ] 데이터 요약 표시

## Vercel
- [ ] Vercel 배포
- [ ] Backend API URL 연결

## README
- [ ] 서비스 소개
- [ ] 기술 스택
- [ ] Frontend 배포 URL
- [ ] Backend API URL
- [ ] Swagger URL
- [ ] 로컬 실행 방법
- [ ] 환경 변수 목록
- [ ] 채팅+데이터 요약 스크린샷
- [ ] CRUD 화면 스크린샷
- [ ] 대화 기록 불러오기 스크린샷

## 보안/운영
- [ ] API Key 환경변수 관리
- [ ] Firebase Key 환경변수 관리
- [ ] 입력값 검증
- [ ] 최소 예외처리
- [ ] API 요청 횟수/토큰 사용 주의
- [ ] 작은 데이터로 먼저 테스트

> **힌트:** 제출 직전 이 체크리스트에서 빈 칸이 필수 항목에 남아 있지 않은지 확인합니다.

---

# 24. 과제 목표에 대한 설명

평가자가 질문할 수 있으므로 README에 짧게 정리해 두는 것을 권장합니다.

## 24-1. 시계열 데이터 분석 → 서비스 활용

```text
[사용자 작성 필요]
원본 데이터를 어떤 기준으로 분석하고 Summary로 만든 뒤,
어떻게 Firestore와 AI 채팅에서 활용했는지 3~5문장으로 작성
```

> **힌트:** “원본 → 전처리 → Summary → Firestore → AI” 순서로 설명합니다.

## 24-2. FastAPI Router / Service 분리 이유

```text
[사용자 작성 필요]
```

> **힌트:** Router는 요청/응답, Service는 비즈니스 로직으로 나눈 이유를 적습니다.

## 24-3. Pydantic 검증 이유

```text
[사용자 작성 필요]
```

> **힌트:** 잘못된 날짜·빈 질문·비정상 값이 DB/API에 들어가는 것을 막기 위해 적용했다고 설명합니다.

## 24-4. Firestore CRUD 설명

```text
[사용자 작성 필요]
```

> **힌트:** `data`와 `conversations`가 각각 무엇을 저장하고 CRUD가 어떻게 작동하는지 적습니다.

## 24-5. Context Injection 설명

```text
[사용자 작성 필요]
```

> **힌트:** GPT가 Firestore를 직접 아는 것이 아니므로 Summary를 System Prompt에 넣는 구조라고 설명합니다.

## 24-6. CORS / 환경변수 / Key 관리가 필요한 이유

```text
[사용자 작성 필요]
```

> **힌트:** Vercel과 Render가 서로 다른 도메인이므로 CORS가 필요하고, Key는 GitHub 노출을 막기 위해 환경변수로 관리한다고 적습니다.

---

# 25. 알려진 한계

초안:

1. 공개 데이터만으로 실제 코레일 좌석의 실시간 잔여 수량이나 과거 예매 오픈 후 매진 속도를 완전히 재현하기 어렵습니다.
2. 따라서 본 서비스의 위험도는 **매진 확률이 아니라 데이터 기반 수요 집중/예매난 참고 지표**입니다.
3. 버스 및 도로 API의 응답 가능 범위나 갱신주기는 제공기관 정책에 따라 달라질 수 있습니다.
4. 실제 이동시간은 사고, 날씨, 임시 운행, 도로상황 등에 따라 달라질 수 있습니다.
5. AI 답변은 저장된 데이터 요약을 바탕으로 한 참고 정보이며 실제 예매 가능 여부는 공식 예매 서비스에서 최종 확인해야 합니다.

**[사용자 작성 필요] 구현 과정에서 발견된 추가 제한사항을 적으세요.**

> **힌트:** 못하는 것을 숨기기보다 정확히 명시하면 서비스 신뢰성이 높아집니다.

---

# 26. 향후 개선 방향

- 코레일 실시간/잔여석 관련 합법적 공식 API가 제공될 경우 연동
- TAGO 고속·시외버스 실시간 정보 강화
- 한국도로공사 실시간 통행시간 연동
- 출발지/도착지와 터미널·역 간 이동시간까지 계산
- 공휴일/연휴/대형행사 변수 자동 반영
- 노선별 맞춤 위험도 모델 개선
- Function Calling을 이용한 KTX/버스/도로 Tool 자동 선택
- MCP Server를 이용한 외부 클라이언트 연결
- 사용자 선호(최단시간/최저비용/환승최소)에 따른 선택지 정렬

> **힌트:** 현재 과제 범위에서 못한 것을 “다음 단계에서 어떻게 발전시킬지” 적습니다.

---

# 27. 과제 수준을 넘어서는 권장 사항

아래는 **필수는 아니지만 잘 된 제출물들에서 특히 도움이 되었던 방식**입니다.

### 27-1. README와 실제 코드 일치 확인
문서에는 있다고 쓰고 코드에는 없는 기능이 생기지 않도록 최종 제출 직전에 다시 대조합니다.

### 27-2. 배포 URL 3개를 README 상단에 바로 표시
```text
Frontend:
Backend:
Swagger:
```

### 27-3. `/health` Endpoint 추가
Render 서버가 정상인지 빠르게 확인할 수 있도록 합니다.

```text
GET /health
→ {"status": "ok"}
```

### 27-4. Timeout 적용
AI API나 외부 공공 API가 응답하지 않을 때 무한 대기하지 않도록 합니다.

### 27-5. 재시도는 제한적으로
AI API 재시도는 1~2회 정도로 제한하고 무한 반복을 방지합니다.

### 27-6. Frontend 안전 출력
사용자 입력/AI 결과를 가능하면 `textContent` 기반으로 출력하고, `innerHTML`을 사용할 경우 사용자 데이터가 그대로 들어가지 않도록 합니다.

### 27-7. Loading 중 중복 전송 방지
AI 답변을 기다리는 동안 전송 버튼을 잠시 비활성화합니다.

### 27-8. 구조화된 AI 응답을 쓸 경우 검증
```text
JSON 여부
→ 필수 Key
→ 자료형
→ 값 범위
→ 화면 출력
```

### 27-9. 모바일 반응형
평가자가 휴대폰에서도 확인할 수 있도록 최소 한 번 모바일 화면을 점검합니다.

### 27-10. 증빙 파일명 통일
예:

```text
01_Service-Home.png
02_AI-Chat.png
03_Data-CRUD.png
04_Conversation-History.png
05_Swagger.png
06_Render.png
07_Vercel.png
08_Mobile.png
09_Bonus-Chart.png
10_Bonus-DarkMode.png
```

### 27-11. 데이터 출처와 갱신일 표시
서비스 화면 또는 README에 “어디서 가져온 데이터인지 / 마지막 갱신일이 언제인지” 표시하면 신뢰성이 높아집니다.

### 27-12. 분석 값의 의미 설명
“예매난 위험도 82”처럼 자체 계산 점수를 사용한다면 점수의 기준과 한계를 사용자가 볼 수 있게 합니다.

---

# 28. 최종 제출 정보

**[사용자 작성 필요]**

```text
프로젝트명:
제출자:
GitHub Repository:
Frontend URL:
Backend API URL:
Swagger URL:

데이터 기간:
데이터 개수:
사용 모델:
최종 업데이트 날짜:
```

> **힌트:** 최종 제출 직전에 실제 URL과 수치로 채웁니다.

---

# 29. 최종 제출 전 1분 점검

- [ ] GitHub에 `.env`가 없다.
- [ ] Firebase Private Key가 없다.
- [ ] API Key가 README/코드/스크린샷에 없다.
- [ ] Frontend URL이 열린다.
- [ ] Backend URL이 열린다.
- [ ] `/docs`가 열린다.
- [ ] AI 질문이 실제 데이터 기반으로 답한다.
- [ ] Loading이 표시된다.
- [ ] Data CRUD가 동작한다.
- [ ] Conversation 저장/불러오기가 동작한다.
- [ ] 데이터 Summary가 화면에 보인다.
- [ ] Render Cold Start 이후 정상 동작한다.
- [ ] README의 기능 설명과 실제 코드가 일치한다.
- [ ] 필수 스크린샷 3장이 README에서 정상 표시된다.
- [ ] 보너스를 적었다면 실제 동작 증거가 있다.
- [ ] “매진 확률”처럼 공개 데이터가 뒷받침하지 않는 표현을 사용하지 않았다.

---

# 30. 구현 완료 후 삭제할 안내문

제출 직전에는 README에서 다음 문구를 삭제하세요.

- `[AI 작성 완료]`
- `[AI 초안]`
- `[사용자 작성 필요]`
- `힌트:`
- 구현하지 않은 보너스 섹션
- 예시용 URL과 예시용 데이터

최종 README에는 **실제 구현 내용과 증빙만 남기는 것**을 권장합니다.
