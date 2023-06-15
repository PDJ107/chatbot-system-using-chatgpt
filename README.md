# chatbot-system-using-chatgpt
LLM을 활용한 질의응답 시스템

### 🗂️ 프로젝트 소개
LLM 중 하나인 ChatGPT의 API와 Langchain을 활용하여 사용자와의 질의응답을 진행합니다. 본 프로젝트에서는 User 인증 및 계정 정보를 처리하는 [API 서버](https://github.com/PDJ107/chatbot-user-api-server)와 질의응답을 처리하는 Chatbot 서버, [안드로이드 APP](https://github.com/KJ-yong/Koreatech-Chat-bot)이 포합됩니다.
<br>

### 📆 개발 기간
* 2023년 3월 1일 ~ 개발중

#### 🙋🏻‍♂️ 멤버 구성
 - 박동주(팀장): 프로젝트 설계, 백엔드 서버 구축, chatbot 시스템 개발
 - [김재용](https://github.com/KJ-yong): 안드로이드 스튜디오를 이용한 챗봇 App 개발
 - [오은솔](https://github.com/oheunsoll): 데이터 수집 모듈 개발 및 프롬프트 작성

#### 🖥️ 개발 환경
 - Apis: `Serp API`, `Google places API`, `ChatGPT API`
 - Develop Platform: `Mac OS 12 Ventura`, `Windows 11`
 - Service: `Android Studio based APP`, `Spring-boot & FastAPI based WEB`, `MySQL`, `elastic search`

#### 🔖 주요 기능
 - 사용자 질문에 대한 답변을 생성하고, APP을 통해 서빙합니다.
   - retrieve: google 검색 엔진 및 elastic search(BM25)기반 context 검색 및 답변 생성
   - action: google 장소 검색, EL 과제 요청, 메시지 예약 등의 태스크 수행

#### 🏢 서비스 아키텍처
<img alt="모듈 구상도" src="img/1. 서비스 아키텍처-1.png">
<img alt="서비스 구상도" src="img/2. 서비스 아키텍처-2.png">

#### 📱 APP 화면
<img alt="APP 화면" src="img/3. APP.png">