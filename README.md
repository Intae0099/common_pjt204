# LawAId - AI 기반 화상 법률 상담 플랫폼 🤖⚖️

> 2030 MZ세대를 위한 AI 법률 상담 웹서비스  
> Spring Boot + Vue.js + FastAPI로 구축된 Full-Stack 애플리케이션

## 📋 목차
- [프로젝트 소개](#프로젝트-소개)
- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [설치 및 실행](#설치-및-실행)
- [API 문서](#api-문서)

## 🚀 프로젝트 소개

**LawAId**는 2030세대가 AI의 도움을 받아 쉽고 빠르게 법률상담을 진행할 수 있는 AI 기반 화상 법률 상담 웹서비스입니다.

### 🎯 개발 배경
- 전체 국민의 56.2%가 법률 문제를 경험했지만, 절반 이상이 상담을 받지 않음 (법률구조공단, 2023)
- 2030세대는 법률 서비스 수요는 있으나 진입장벽이 높다고 인식
- 비대면 환경에서 **화상 미팅**, **AI 법률 지원**, **자동 문서 생성**이 통합된 올인원 플랫폼 필요

### 🎯 타겟 사용자
**2030 MZ세대** - 디지털 네이티브, 초기 사회 진입층, 모바일 기반 셀프 리서처

## ✨ 주요 기능

### 🎥 실시간 화상 상담 (WebRTC)
- OpenVidu 기반 1:1 화상 연결
- 상담 상태 제어 및 세션 관리
- 상담 매칭 및 요청/수락 시스템
- 실시간 채팅 기능 통합

### 🤖 AI 기반 사전 상담
- LangChain + OpenAI 기반 법률 상담 챗봇
- FAQ 기반 질의응답 시스템
- WebSocket을 통한 실시간 채팅 인터페이스
- 벡터 검색을 활용한 유사 사례 추천

### 📊 판례 검색 및 분석
- 법원 판례 데이터 벡터화 및 검색
- FAISS + Sentence Transformers 기반 유사도 검색
- 판례 상세 정보 및 분석 결과 제공

### 📄 AI 기반 문서 자동 생성
- 사건 개요 입력 시 상담 신청서 자동 생성
- 구조화된 법률 문서 템플릿 제공
- 마이페이지에서 문서 관리 및 다운로드

### 📅 상담 예약 및 일정 관리
- 변호사 캘린더 기반 예약 시스템
- 사용자/변호사 일정 확인 및 관리
- 상담 요청 수락/거절 기능
- 예약 알림 및 상태 관리

## 🛠 기술 스택

### Frontend
- **Vue.js 3** + Vite
- **Pinia** (상태 관리)
- **Vue Router** (라우팅)
- **Bootstrap 5** (UI 프레임워크)
- **OpenVidu Browser** (화상 통화)
- **Socket.IO Client** (실시간 통신)

### Backend
- **Spring Boot 3.5.3** + Java 21
- **Spring Security** + JWT
- **Spring Data JPA**
- **MySQL** (데이터베이스)
- **OAuth2** (소셜 로그인)
- **Swagger/OpenAPI** (API 문서)

### AI Service
- **FastAPI** (웹 프레임워크)
- **LangChain** (LLM 체인)
- **OpenAI GPT** (언어 모델)
- **Sentence Transformers** (임베딩)
- **FAISS** (벡터 검색)
- **PostgreSQL + pgvector** (벡터 DB)

### DevOps & Infrastructure
- **Docker** + **Docker Compose**
- **Jenkins** (CI/CD)
- **Nginx** (리버스 프록시)

## 🚀 설치 및 실행

### 필수 조건
- **Node.js** 18+
- **Java** 21+
- **Python** 3.9+
- **Docker** & **Docker Compose**
- **MySQL** 8.0+

### 1. 저장소 클론
```bash
git clone https://github.com/your-org/lawaid.git
cd lawaid
```

### 2. Docker를 이용한 통합 실행
```bash
docker-compose up -d
```

### 3. 개별 서비스 실행

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Backend
```bash
cd backend
./mvnw spring-boot:run
```

#### AI Service
```bash
cd ai
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. 애플리케이션 접속
- **Application**: https://i13b204.p.ssafy.io
- **Backend API**: https://i13b204.p.ssafy.io/swagger-ui/index.html
- **AI Service**: http://122.38.210.80:8997/docs

## 📚 API 문서

### 주요 엔드포인트

#### 사용자 관리
- `POST /api/auth/login` - 로그인
- `POST /api/auth/signup` - 회원가입
- `GET /api/users/profile` - 프로필 조회

#### 상담 관리
- `POST /api/applications` - 상담 신청
- `GET /api/appointments` - 예약 목록
- `PUT /api/appointments/{id}/status` - 예약 상태 변경

#### 화상 상담
- `POST /api/rooms` - 상담방 생성
- `POST /api/rooms/{id}/join` - 상담방 참여
- `DELETE /api/rooms/{id}/leave` - 상담방 퇴장

#### AI 서비스
- `POST /ai/chat` - AI 상담
- `POST /ai/documents/generate` - 문서 생성
- `GET /ai/cases/search` - 판례 검색

자세한 API 문서는 [Swagger UI](https://i13b204.p.ssafy.io/swagger-ui/index.html)와 [OpenAPI UI](http://122.38.210.80:8997/docs)에서 확인 가능합니다.


## 📖 용어 정리

| 용어 | 정의 |
|------|------|
| **WebRTC** | 웹 브라우저 간 플러그인 없이 실시간 통신을 가능하게 하는 API |
| **WebSocket** | 단일 TCP 연결로 양방향 통신 채널을 제공하는 프로토콜 |
| **판례** | 법원에서 동일하거나 비슷한 사건에 대해 내린 재판의 선례 |
| **JWT** | JSON Web Token, 인증 정보를 안전하게 전송하기 위한 표준 |
| **Vector Search** | 벡터 공간에서 유사도 기반 검색을 수행하는 기술 |
| **LangChain** | 대화형 AI 애플리케이션 개발을 위한 프레임워크 |