# GreenAI Dashboard

실시간 객체 감지 데이터 파이프라인 대시보드

## 프로젝트 개요

본 프로젝트는 실시간 데이터 수신 → 저장/집계 → 대시보드 실시간 갱신 흐름을 구현한 풀스택 애플리케이션입니다.

### 주요 기능

- **데이터 수집**: REST API를 통한 감지 데이터 수신
- **실시간 집계**: 시간 범위별 통계 계산 및 제공
- **실시간 대시보드**: WebSocket을 통한 2초 간격 KPI 자동 갱신
- **타입별 분석**: 보행자, 자전거, 차량, 대형차량 감지 통계

## 기술 스택

### Backend
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **SQLAlchemy**: ORM 및 데이터베이스 관리
- **SQLite**: 경량 데이터베이스
- **WebSocket**: 실시간 양방향 통신

### Frontend
- **React 18**: UI 라이브러리
- **TypeScript**: 타입 안전성
- **Vite**: 빠른 개발 서버 및 빌드

### Infrastructure
- **Docker & Docker Compose**: 컨테이너화 및 오케스트레이션

## 프로젝트 구조

```
GreenAI-Dashboard/
├── backend/              # FastAPI 백엔드
│   ├── main.py          # FastAPI 애플리케이션
│   ├── database.py      # 데이터베이스 모델
│   ├── models.py        # Pydantic 스키마
│   └── requirements.txt # Python 의존성
├── frontend/            # React 프론트엔드
│   ├── src/
│   │   ├── components/  # React 컴포넌트
│   │   ├── hooks/       # 커스텀 훅
│   │   └── types.ts     # TypeScript 타입
│   └── package.json     # npm 의존성
├── docker-compose.yml   # Docker Compose 설정
└── README.md
```

## 실행 방법

### Docker Compose (권장)

```bash
docker-compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000

### 개별 실행

**백엔드:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**프론트엔드:**
```bash
cd frontend
npm install
npm run dev
```

## API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 라이센스

MIT License