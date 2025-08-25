# 포팅메뉴얼

<br>

### 1. Gitlab 소스 클론 이후 빌드 및 배포 문서

이 문서는 새로운 담당자가 프로젝트 소스 코드를 내려받아 로컬 또는 서버 환경에 빌드하고 배포하는 전체 과정을 안내합니다.

<br>
<br>
<br>

#### 1) 시스템 및 소프트웨어 구성

프로젝트를 구동하는 데 필요한 주요 소프트웨어와 개발 환경 정보입니다.

| 구분 | 제품명 | 버전 | 설정 값 / 참고사항 |
| --- | --- | --- | --- |
| **개발 IDE** | | | |
| | IntelliJ IDEA | 2024.01 | |
| | Visual Studio Code | 1.103.1 | Vue 개발용 확장 프로그램: `Volar`, `ESLint` |
| **언어 (Language)** | | | |
| | Java (JVM) | 21 | Spring Boot 실행에 사용 |
| | Python | 3.11 | FastAPI 실행에 사용 |
| **백엔드 (Backend)** | | | |
| | Spring Boot | 3.5.3 | |
| | JPA (Hibernate) | 6.6.18 | |
| | FastAPI | 0.116.1 | |
| **프론트엔드 (Frontend)** | | | |
| | Vue.js | 3.4.29 | 메인 프레임워크 |
| | Node.js | 22.17.1 | Vue 프로젝트 빌드 시 필요 |
| | Vite | 5.2.13 | 개발 및 빌드 도구 |
| | Vue Router | 4.3.3 | 라우팅 관리 |
| | Pinia | 2.3.1 | 상태 관리 라이브러리 |
| **데이터베이스 (DB)** | | | |
| | MySQL | 8.0.41 | |
| **웹 서버 (Web Server)** | | | |
| | Nginx | nginx/1.29.0 | Reverse Proxy로 사용, 설정 파일은 `~/proxy/conf.d/default.conf` |
| **WAS** | | | |
| | 내장 Tomcat | 10.1.42 | Spring Boot에 내장되어 별도 설치 불필요 |
| **인프라 (Infra)** | | | |
| | GitLab | | 소스 코드 관리 |
| | Jenkins | 2.504.3 | |
| | Docker | Docker version 28.3.2 | |
| | OpenVidu | 2.30.0 | |

<br>
<br>
<br>

#### 2) 빌드 시 환경 변수

Jenkins 또는 로컬에서 프로젝트 빌드 시 필요한 환경 변수 목록입니다.

- **Spring Boot (Backend)**
    - `src/main/resources/application.properties` 파일에 정의된 환경 변수들을 기재합니다.
    - **DB 연결 정보**
        - `SPRING_DATASOURCE_URL`: `jdbc:mysql://my-mysql:3306/alawdb?serverTimezone=Asia/Seoul&useSSL=false`
        - `SPRING_DATASOURCE_USERNAME`: `admin`
        - `SPRING_DATASOURCE_PASSWORD`: `99990000001`
    - **기타**
        - `OPENVIDU_URL`: `https://i13b204.p.ssafy.io`
        - `OPENVIDU_SECRET`: `ssafy204openvidulawaid`
- **Vue.js (Frontend)**
    - 프로젝트 루트의 `.env.production` 파일에 정의된 환경 변수들을 기재합니다.
    - `VITE_API_URL`: `https://i13b204.p.ssafy.io/api`
    - `VITE_FAST_API_URL`: `https://i13b204.p.ssafy.io/api-fast`
    - `VITE_OPENVIDU_URL`: `https://i13b204.p.ssafy.io`
- **Jenkins**
    - Jenkins 빌드 파이프라인(`Jenkinsfile`)에서 사용하는 환경 변수나 Credential 정보를 기재합니다.
    - **GitLab Repository Access id**: `gitlab-repo-credentials`
    - **GitLab API token (GitLab API Access Token) id**: `gitlab-api-token`
    - **GitLab Registry Login Credentials id**: `gitlab-registry-credentials`

<br>
<br>
<br>

#### 3) 배포 시 특이사항

1.  **CI/CD 파이프라인**
    - 전체 흐름: `GitLab Push (main 브랜치)` -> `GitLab Webhook` -> `Jenkins Pipeline Trigger` -> `Vue, Spring Boot 빌드 및 Docker Image 생성` -> `AWS ECR에 이미지 Push` -> `EC2 서버에서 최신 이미지 Pull 및 컨테이너 재시작`
    - Jenkins 파이프라인 스크립트는 프로젝트 내 `Jenkinsfile`에 정의되어 있습니다.
2.  **Nginx Reverse Proxy**
    - 제공된 `~/proxy/conf.d/default.conf` 설정 파일에 따라 모든 트래픽이 분기됩니다.
    - SSL 인증서는 Let's Encrypt를 통해 발급받았으며, 자동 갱신 설정이 필요할 수 있습니다.
    - `/api/` 경로는 Spring Boot, `/api-fast/`는 FastAPI, `/jenkins/`는 Jenkins, `/openvidu/`는 OpenVidu로 프록시됩니다. 나머지 모든 요청은 Vue 프론트엔드로 전달됩니다.
3.  **Docker 실행**
    - EC2 서버에서는 `docker-compose.yml` 파일을 통해 각 서비스(frontend, backend, mysql 등)를 컨테이너로 실행합니다.
    - 배포 스크립트 실행 시 기존 컨테이너를 내리고 새로운 이미지로 컨테이너를 올리는 작업이 포함됩니다.
<br>
<br>
<br>

#### 4) 주요 계정 및 프로퍼티 정의 파일 목록

| 파일 경로 | 주요 내용 |
| --- | --- |
| `backend/src/main/resources/application.properties` | DB 접속 정보, JWT 시크릿, OAuth2 클라이언트 ID/Secret 등 백엔드의 모든 설정 |
| `frontend/.env` | 프론트엔드에서 사용하는 백엔드 API 서버 주소 등 환경별 설정 |
| `Jenkinsfile` | Jenkins CI/CD 파이프라인 스크립트 (빌드, 이미지 푸시, 배포) |
| `/home/ubuntu/app/docker-compose.yml` | 각 서비스의 Docker 컨테이너 실행 및 네트워크 구성 정의 |
| `proxy/conf.d/default.conf` | Nginx 리버스 프록시 라우팅 규칙 정의 |

<br>
<br>
<br>

---


<br>
<br>
<br>

### 2. 외부 서비스 정보

프로젝트가 의존하는 외부 클라우드 서비스 및 API 정보입니다.

| 서비스명 | 용도 | 가입/설정 URL | 계정 정보 | API Key / Secret | 주요 설정값 |
| --- | --- | --- | --- | --- | --- |
| **카카오 소셜 로그인** | 사용자 인증 | https://developers.kakao.com/ | rbtjd1478@naver.com | ~~**REST API 키:** `[ 발급받은 키 ]`<br>**Client Secret:** `[ 발급받은 시크릿 ]`~~ | **Redirect URI:**<br>`https://i13b204.p.ssafy.io/api/login/oauth2/code/kakao` |
| **OpenVidu** | 화상 통화 | 자체 호스팅 (Self-hosted) | - | **OPENVIDU_SECRET:** `ssafy204openvidulawaid` | **DOMAIN_OR_PUBLIC_IP:**<br>`https://i13b204.p.ssafy.io/openvidu` |
| **AWS EC2** | 서버 호스팅 | i13b204.p.ssafy.io | - | - | `I13B204T.pem` |
<br>  
<br>  
<br>
 
### 3. DB 덤프 파일 최신본

# [DB 덤프 파일](https://lab.ssafy.com/s13-webmobile1-sub1/S13P11B204/-/blob/master/lawaid%20schema.sql?ref_type=heads)

<br>  
<br>  
<br> 

### 4. 시연 시나리오

#### 애플리케이션 기능 및 관련 컴포넌트 정리

| 기능/메뉴 | 주요 동작 및 설명 | 관련 Vue 컴포넌트 |
| --- | --- | --- |
| **메인 페이지** | 사용자가 사이트에 처음 접속했을 때 표시되는 페이지. 네비게이션 바와 푸터가 포함됨. | `MainPageView.vue`, `BaseNavbar.vue`, `BaseFooter.vue` |
| **사건 검색** | 사건 목록을 카드 형태로 확인하고, 특정 사건 클릭 시 상세 정보 페이지로 이동. | `CaseSearchPage.vue`, `CaseCard.vue`, `CaseDetail.vue` |
| **AI 상담** | 챗봇 인터페이스를 통해 AI에게 질문하고 답변을 받으며, 추천 변호사 목록 확인 가능. | `AIStep.vue`, `ChatbotView.vue`, `LawyerRecommendList.vue` |
| **상담 예약** | 예약 폼을 작성하고 변호사 목록에서 원하는 변호사를 선택하여 상담 예약 완료. | `ConsultationFormView.vue`, `LawyerSearch.vue` |
| **실시간 채팅** | 예약이 완료된 변호사와 텍스트 기반으로 실시간 상담 진행. | `RealtimeChatView.vue` |
| **화상 회의** | 필요 시, 변호사와 영상 및 음성을 통해 화상으로 상담 진행. | `MeetingRoom.vue` |
| **마이페이지** | 자신의 상담 내역과 프로필 정보를 확인하고 수정. | `LawyerMyPage.vue`, `UserMyPage.vue` (및 기타 마이페이지 관련 컴포넌트) |
| **관리자 기능** | 관리자 전용 페이지(`/admin`)에서 회원, 사건, 변호사 인증 등 사이트 전반을 관리. | `AdminLayout.vue` (및 기타 관리자 페이지 관련 컴포넌트) |
| **공통/레이아웃** | 특정 페이지(관리자, 메인, 사건 상세 등)에서는 푸터를 숨기고, 그 외 페이지에서는 노출. | `BaseFooter.vue`, `BaseNavbar.vue` (노출/비노출 로직은 `App.vue` 또는 라우터에서 제어) |

<br>
<br>
<br>