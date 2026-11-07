# KTX 수요 분석 서비스 화면 목록

## 제출용 Vercel 화면

[제출 서비스 열기](https://ktx-congestion-analysis-frontend.vercel.app) · [프로젝트 설명으로 돌아가기](README.md)

| 번호 | 화면 | 확인할 내용 |
|---|---|---|
| 30 | [데이터 요약과 AI 대화](image/30_vercel_summary_chat.jpg) | 월별 승차 수요 요약과 사용자 질문에 대한 답변 |
| 31 | [데이터 관리](image/31_vercel_crud.jpg) | 2024-01-01 테스트 행을 추가한 화면과 삭제한 화면을 차례로 발췌 |
| 32 | [저장된 대화](image/32_vercel_conversation.jpg) | 최근 대화 목록과 선택한 대화 내용 |

## 로컬 데이터 처리와 API 확인

| 번호 | 화면 | 확인할 내용 |
|---|---|---|
| 01 | [KTX 데이터 전처리](image/01_DataPreprocessing_전처리결과확인.jpg) | 원본 CSV를 역·방향별 월 승차 기록으로 변환한 실행 결과 |
| 02 | [분석 요약](image/02_DataAnalysis_분석Summary확인.jpg) | 분석 기간, 레코드 수와 월별 수요 통계 |
| 03 | [Firestore 초기 데이터 적재](image/03_FirestoreSeed_168건업로드성공.jpg) | 전국 KTX 월별 집계 168건을 업로드한 실행 결과 |
| 04 | [데이터 API 목록](image/04_DataAPI_Swagger_CRUD엔드포인트.jpg) | 로컬 Swagger에 표시된 데이터 조회·추가·수정·삭제 경로 |
| 05 | [데이터 추가 테스트](image/05_DataAPI_POST_데이터추가테스트.jpg) | POST 요청으로 테스트 데이터를 추가한 결과 |
| 06 | [대화 API 목록](image/06_ConversationAPI_Swagger_엔드포인트.jpg) | 로컬 Swagger에 표시된 대화 저장·조회·삭제 경로 |
| 07 | [Firestore 요약을 사용한 AI 응답](image/07_OpenAI_FirestoreSummary_연결성공.jpg) | 연결 테스트에서 출력한 데이터 요약과 답변 |
| 08 | [프런트엔드 초기 화면](image/08_Frontend_UI_초기화면구현.jpg) | 로컬 파일로 연 초기 질문 입력 화면 |
| 09 | [AI 답변과 최근 대화 목록](image/09_Frontend_Chat_AI응답_최근대화갱신.jpg) | 로컬 서버에서 질문을 전송한 뒤 표시된 답변과 대화 목록 |
| 16 | [Git 추적 상태 확인](image/16_Git_보안파일제외_최종점검.jpg) | 로컬 저장소에서 비밀 설정 파일의 Git 추적 여부를 확인한 기록 |

## 기존 Render 배포와 연결 점검

10~15번은 Render 백엔드와 당시 Render 정적 프런트엔드에서 진행한 확인 기록입니다. 12번과 13번을 차례로 보면 브라우저의 대화 조회 오류와 설정 변경 후의 화면을 비교할 수 있습니다.

| 번호 | 화면 | 확인할 내용 |
|---|---|---|
| 10 | [배포한 백엔드의 Swagger](image/10_Render_Backend_Swagger_외부접속.jpg) | Render 백엔드의 공개 문서 페이지 |
| 11 | [정적 프런트엔드 배포](image/11_Render_Frontend_StaticSite_배포성공.jpg) | Render 대시보드에 표시된 정적 사이트 배포 결과 |
| 12 | [대화 조회 오류](image/12_Render_Frontend_CORS오류_FailedToFetch.jpg) | 브라우저에 표시된 `Failed to fetch` 메시지 |
| 13 | [CORS 설정 변경 후 대화 조회](image/13_Render_Frontend_CORS해결_최근대화조회.jpg) | Render 프런트엔드에서 다시 불러온 최근 대화 목록 |
| 14 | [대체 이동수단 질문에 대한 답변](image/14_Render_Frontend_최종통합테스트_AI응답.jpg) | KTX 대신 버스나 자가용을 선택할 때 필요한 추가 데이터 설명 |
| 15 | [질문 전송 후 대화 목록 갱신](image/15_Render_Frontend_Firestore저장_최근대화갱신.jpg) | 답변을 받은 뒤 최근 대화 목록에 추가된 항목 |

## 로컬 프런트엔드 기능 확인

17~25번은 주소창에 `127.0.0.1:5500`이 표시된 로컬 화면입니다. 19~24번은 테스트용 월 데이터를 한 건 추가하고 삭제하는 과정을 순서대로 보여 줍니다.

| 번호 | 화면 | 확인할 내용 |
|---|---|---|
| 17 | [월별 데이터 요약](image/17_Frontend_DataSummary_요약정보표시성공.jpg) | 프런트엔드에 표시된 수요 요약 |
| 18 | [데이터 목록과 원본 보호 표시](image/18_Frontend_CRUD_UI_데이터목록_원본보호확인.jpg) | 원본 데이터 목록과 보호 상태 |
| 19 | [테스트 데이터 입력](image/19_Frontend_CRUD_테스트데이터입력완료.jpg) | 추가할 월, 승차인원, 메모를 입력한 상태 |
| 20 | [추가 요청 전송](image/20_Frontend_CRUD_테스트데이터_POST추가중.jpg) | POST 요청을 처리하는 동안의 화면 |
| 21 | [테스트 데이터 추가 결과](image/21_Frontend_CRUD_테스트데이터추가성공.jpg) | 추가 요청 이후의 성공 메시지 |
| 22 | [추가 후 목록 새로고침](image/22_Frontend_CRUD_데이터목록새로고침_169건확인.jpg) | 테스트 데이터 한 건을 포함해 169건이 된 목록 |
| 23 | [테스트 데이터 삭제 확인](image/23_Frontend_CRUD_테스트데이터삭제확인_원본168건보호.jpg) | 선택한 테스트 행에 대한 삭제 확인 창 |
| 24 | [삭제 후 원본 목록 확인](image/24_Frontend_CRUD_테스트데이터삭제성공_원본데이터복구.jpg) | 테스트 행을 지운 뒤 168건으로 돌아온 목록 |
| 25 | [저장된 대화 불러오기](image/25_Frontend_Conversation_특정대화불러오기성공.jpg) | 최근 대화에서 선택한 질문과 답변 |
