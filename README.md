# GreenAI Dashboard

실시간 데이터 감지 파이프라인 대시보드

## 프로젝트 개요

실시간 데이터 수신 → 저장/집계 → 대시보드 실시간 갱신 흐름을 구현.

### 주요 기능

- **데이터 수집**: REST API를 통한 감지 데이터 수신
- **실시간 집계**: 시간 범위별 통계 계산 및 제공
- **실시간 대시보드**: WebSocket을 통한 2초 간격 KPI 자동 갱신
- **타입별 분석**: 보행자, 자전거, 차량, 대형차량 감지 통계

## 기술 스택

### Backend
- **FastAPI**
- **SQLAlchemy**: ORM 및 데이터베이스 관리
- **SQLite**: 경량 데이터베이스
- **WebSocket**

### Frontend
- **React 18**
- **TypeScript**
- **Vite**

### Infrastructure
- **Docker & Docker Compose**: 컨테이너화 및 오케스트레이션

## 프로젝트 구조

```
GreenAI-Dashboard/
├── backend/              # FastAPI 백엔드
│   ├── main.py          
│   ├── database.py      
│   ├── models.py        
│   └── requirements.txt 
├── frontend/            # React 프론트엔드
│   ├── src/
│   │   ├── components/  
│   │   ├── hooks/       
│   │   └── types.ts     
│   └── package.json     
├── docker-compose.yml   # Docker Compose 설정
└── README.md
```