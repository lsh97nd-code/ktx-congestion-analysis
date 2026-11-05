# 코드 검토 및 Render 프런트엔드 오류 수정

기준 커밋: `3865a37` (Configure frontend API URL with Vercel environment variable).

## 확인된 사이트 장애

- Frontend HTML: HTTP 200.
- `https://ktx-congestion-analysis-frontend.onrender.com/js/config.js`: HTTP 404.
- Backend `/health`, `/api/data/summary`: HTTP 200. Frontend Origin에 대한 CORS 허용 헤더도 정상.
- `index.html`은 `js/config.js`를 참조하지만 해당 파일은 기존 `build.js`가 `dist/`에만 생성했습니다. Render의 무빌드·원본 폴더 배포에서는 파일이 없어 `app.js` 최상위에서 예외가 발생하고 모든 화면 초기화가 중단됐습니다.

수정: 직접 정적 배포용 `frontend/js/config.js`를 추가했습니다. 로컬 호스트는 로컬 API, 외부 호스트는 기존 Render API를 사용합니다. 환경별 빌드는 계속 `API_BASE_URL`로 `dist/js/config.js`를 생성합니다. 설정 누락 시에는 화면에 오류를 표시합니다.

## 함께 수정한 문제

| 우선순위 | 문제 | 수정 |
|---|---|---|
| P1 | 원본 보호가 프런트엔드 버튼에만 있어 직접 API로 삭제·변경 가능 | 2023-12까지 API 쓰기 403, 문서 ID 형식 검증 |
| P1 | 누락된 월이 있어도 마지막 24개 레코드를 24개월로 계산 | 연속 24개월 검증, 0 기준 변화율은 계산 불가 |
| P1 | 동시 생성의 get/set 사이에 기존 월 데이터 덮어쓰기 가능 | Firestore atomic create, 충돌 409 |
| P2 | 일 단위 날짜·소수 승차인원 허용 및 저장된 값의 정수 절삭 | 월 시작일·음이 아닌 정수 검증, 화면 월 입력 |
| P2 | 전처리의 누락·음수·중복 값으로 집계 왜곡 가능 | 날짜·역·승하차 인원·중복 조합 검증 |
| P2 | 최근 대화 조회가 전체 컬렉션을 읽고 저장소 장애는 비정형 500 | DB 조회 기본 20건/최대 100건, 통일된 503 및 404 유지 |
| P2 | OpenAI의 미완료 응답 일부를 정상 답변으로 저장 가능 | Responses 상태가 completed일 때만 텍스트 반환 |
| P2 | OpenAI 설정 로더가 상위 프로젝트의 .env를 탐색 가능 | 이 프로젝트의 .env만 명시적으로 로드 |

OpenAI 상태 처리는 [공식 Responses API 문서](https://developers.openai.com/api/reference/python/resources/responses/methods/create)를 기준으로 검토했습니다.

## 검증

- Python 회귀 테스트 80개 통과: API 보호·오류, 대화 조회 제한, 월별 연속성, 입력 검증, 원자적 생성, OpenAI 완료 상태, 설정 범위.
- Frontend Node 테스트 24개 통과: 무빌드 배포의 정적 파일, 환경별 API 설정, 빌드 URL 검증, 설정 누락 화면, 월별 입력 검증.
- 저장소의 실제 가공 데이터 재분석: 기존 공개 분석 결과 및 168개월 데이터와 일치.
- 테스트는 실제 Firestore 변경이나 유료 OpenAI 요청을 수행하지 않습니다. 운영 AI 응답·저장 전체 흐름은 이번 수정 검증에서 호출하지 않았습니다.

## 공개 시연에서 유지한 제한

사용자 선택에 따라 인증은 추가하지 않았습니다. 대화는 모든 방문자가 공유하며 조회·작성·삭제할 수 있습니다. 2024년 이후 테스트 데이터도 공유되고 데이터 요약 및 AI 답변에 영향을 줍니다. 사용자별 권한·호출량 제한이 없어 API 호출 비용 및 악용 위험이 남습니다. 개인정보와 비밀정보를 입력하지 않는 공개 시연으로 사용해야 합니다.

## 배포 반영

로컬 파일 수정만으로 기존 Render 사이트는 바뀌지 않습니다. 변경사항을 GitHub에 반영한 뒤 연결된 Render 서비스의 배포를 완료해야 합니다. 기존 무빌드 배포 설정도 새 `frontend/js/config.js`를 포함하면 작동하며, 환경별 주소를 쓸 때는 README의 build/dist 설정을 사용합니다.
