from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import asyncio
import json

from database import engine, get_db, Base
from models import Detection

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GreenAI Dashboard API",
    description="실시간 객체 감지 데이터 수집 및 통계 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass


manager = ConnectionManager()


# Pydantic 모델 정의
class DetectedObject(BaseModel):
    """개별 객체 정보"""
    uuid: str = Field(..., description="객체 고유 ID")
    type: str = Field(..., description="객체 타입: Pedestrian, Bike, Vehicle, LargeVehicle")
    x: float = Field(..., description="x 좌표")
    y: float = Field(..., description="y 좌표")
    speed_ms: Optional[float] = Field(None, description="속도 (m/s)")

    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "abc-123",
                "type": "Pedestrian",
                "x": 12.5,
                "y": 3.2,
                "speed_ms": 1.2
            }
        }


class IngestData(BaseModel):
    """데이터 수신용 모델"""
    timestamp: str = Field(..., description="감지 시각 (ISO 8601)")
    zone: str = Field(..., description="감지 구역")
    objects: List[DetectedObject] = Field(..., description="감지된 객체 배열")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-02-12T14:30:00",
                "zone": "A구역",
                "objects": [
                    {"uuid": "abc-123", "type": "Pedestrian", "x": 12.5, "y": 3.2, "speed_ms": 1.2},
                    {"uuid": "def-456", "type": "Vehicle", "x": 45.1, "y": 8.7, "speed_ms": 8.3}
                ]
            }
        }


class ObjectTypeStats(BaseModel):
    """객체 타입별 통계"""
    type: str
    count: int
    avg_speed: Optional[float] = None


class StatsResponse(BaseModel):
    """통계 응답 모델"""
    total_count: int
    avg_speed: Optional[float]
    by_type: List[ObjectTypeStats]
    from_time: datetime
    to_time: datetime
    zone: Optional[str] = None


class KPIData(BaseModel):
    """실시간 KPI 데이터"""
    total_count: int
    avg_speed: Optional[float]
    by_type: List[ObjectTypeStats]
    timestamp: datetime


@app.get("/")
async def root():
    """헬스 체크 엔드포인트"""
    return {
        "message": "GreenAI Dashboard API",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/ingest", status_code=201)
async def ingest_detection(
    data: IngestData,
    db: Session = Depends(get_db)
):
    """
    객체 감지 데이터 수신 엔드포인트

    샘플 데이터 형식:
    {
        "timestamp": "2026-02-12T14:30:00",
        "zone": "A구역",
        "objects": [
            {"uuid": "abc-123", "type": "Pedestrian", "x": 12.5, "y": 3.2, "speed_ms": 1.2}
        ]
    }
    """
    # 유효한 객체 타입 검증
    valid_types = ['Pedestrian', 'Bike', 'Vehicle', 'LargeVehicle']

    # timestamp 파싱
    try:
        timestamp = datetime.fromisoformat(data.timestamp.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid timestamp format. Use ISO 8601 format."
        )

    # 각 객체를 DB에 저장
    saved_objects = []
    for obj in data.objects:
        if obj.type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid object type '{obj.type}'. Must be one of: {', '.join(valid_types)}"
            )

        db_detection = Detection(
            timestamp=timestamp,
            zone=data.zone,
            uuid=obj.uuid,
            object_type=obj.type,
            x=obj.x,
            y=obj.y,
            speed_ms=obj.speed_ms
        )
        db.add(db_detection)
        saved_objects.append({
            "uuid": obj.uuid,
            "type": obj.type
        })

    db.commit()

    # WebSocket으로 최신 KPI 전송 (비동기)
    asyncio.create_task(broadcast_latest_kpi(db))

    return {
        "message": "Detection data ingested successfully",
        "timestamp": timestamp,
        "zone": data.zone,
        "objects_count": len(saved_objects),
        "objects": saved_objects
    }


@app.get("/stats", response_model=StatsResponse)
async def get_stats(
    from_time: Optional[str] = Query(None, description="시작 시각 (ISO 8601)"),
    to_time: Optional[str] = Query(None, description="종료 시각 (ISO 8601)"),
    zone: Optional[str] = Query(None, description="구역 필터 (예: A구역)"),
    db: Session = Depends(get_db)
):
    """
    지정된 시간 범위의 감지 통계 조회

    - from: 시작 시각 (ISO 8601)
    - to: 종료 시각 (ISO 8601)
    - zone: 구역 필터 (선택)
    - 총 객체 수, 타입별 개수 및 평균 속도 반환
    - 데이터가 없을 경우 count: 0, avg_speed: null 반환
    """
    # 시간 범위 파싱
    try:
        if from_time:
            start_time = datetime.fromisoformat(from_time.replace('Z', '+00:00'))
        else:
            # 기본값: 최근 5분
            start_time = datetime.utcnow().replace(minute=datetime.utcnow().minute - 5)

        if to_time:
            end_time = datetime.fromisoformat(to_time.replace('Z', '+00:00'))
        else:
            # 기본값: 현재 시각
            end_time = datetime.utcnow()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid datetime format. Use ISO 8601 format."
        )

    # 쿼리 구성
    query = db.query(Detection).filter(
        Detection.timestamp >= start_time,
        Detection.timestamp <= end_time
    )

    if zone:
        query = query.filter(Detection.zone == zone)

    # 총 객체 수 조회
    total_count = query.count()

    # 전체 평균 속도 조회
    avg_speed_result = query.with_entities(
        func.avg(Detection.speed_ms)
    ).scalar()
    avg_speed = round(avg_speed_result, 2) if avg_speed_result else None

    # 타입별 통계 조회
    type_stats_query = query.with_entities(
        Detection.object_type,
        func.count(Detection.id).label('count'),
        func.avg(Detection.speed_ms).label('avg_speed')
    ).group_by(Detection.object_type).all()

    # 응답 데이터 구성
    by_type = []
    for stat in type_stats_query:
        by_type.append(ObjectTypeStats(
            type=stat.object_type,
            count=stat.count,
            avg_speed=round(stat.avg_speed, 2) if stat.avg_speed else None
        ))

    return StatsResponse(
        total_count=total_count,
        avg_speed=avg_speed,
        by_type=by_type,
        from_time=start_time,
        to_time=end_time,
        zone=zone
    )


async def broadcast_latest_kpi(db: Session):
    """최신 KPI 데이터를 WebSocket으로 브로드캐스트"""
    try:
        # 최근 5분 데이터 조회
        end_time = datetime.utcnow()
        start_time = end_time.replace(minute=end_time.minute - 5)

        query = db.query(Detection).filter(
            Detection.timestamp >= start_time,
            Detection.timestamp <= end_time
        )

        total_count = query.count()
        avg_speed_result = query.with_entities(func.avg(Detection.speed_ms)).scalar()
        avg_speed = round(avg_speed_result, 2) if avg_speed_result else None

        type_stats_query = query.with_entities(
            Detection.object_type,
            func.count(Detection.id).label('count'),
            func.avg(Detection.speed_ms).label('avg_speed')
        ).group_by(Detection.object_type).all()

        by_type = []
        for stat in type_stats_query:
            by_type.append({
                "type": stat.object_type,
                "count": stat.count,
                "avg_speed": round(stat.avg_speed, 2) if stat.avg_speed else None
            })

        kpi_data = {
            "total_count": total_count,
            "avg_speed": avg_speed,
            "by_type": by_type,
            "timestamp": datetime.utcnow().isoformat()
        }

        await manager.broadcast(json.dumps(kpi_data))
    except Exception as e:
        print(f"Error broadcasting KPI: {e}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 엔드포인트 - 2초마다 최신 KPI 전송

    프론트엔드에서 연결하여 실시간 KPI 업데이트 수신
    """
    await manager.connect(websocket)
    db = next(get_db())

    try:
        while True:
            # 최근 5분 데이터 조회
            end_time = datetime.utcnow()
            start_time = end_time.replace(minute=max(0, end_time.minute - 5))

            query = db.query(Detection).filter(
                Detection.timestamp >= start_time,
                Detection.timestamp <= end_time
            )

            total_count = query.count()
            avg_speed_result = query.with_entities(func.avg(Detection.speed_ms)).scalar()
            avg_speed = round(avg_speed_result, 2) if avg_speed_result else None

            type_stats_query = query.with_entities(
                Detection.object_type,
                func.count(Detection.id).label('count'),
                func.avg(Detection.speed_ms).label('avg_speed')
            ).group_by(Detection.object_type).all()

            by_type = []
            for stat in type_stats_query:
                by_type.append({
                    "type": stat.object_type,
                    "count": stat.count,
                    "avg_speed": round(stat.avg_speed, 2) if stat.avg_speed else None
                })

            kpi_data = {
                "total_count": total_count,
                "avg_speed": avg_speed,
                "by_type": by_type,
                "timestamp": datetime.utcnow().isoformat()
            }

            await websocket.send_text(json.dumps(kpi_data))
            await asyncio.sleep(2)  # 2초 간격

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        db.close()


@app.delete("/detections", status_code=200)
async def delete_all_detections(db: Session = Depends(get_db)):
    """
    모든 감지 데이터 삭제 (테스트/개발용)
    """
    deleted_count = db.query(Detection).delete()
    db.commit()

    return {
        "message": f"Deleted {deleted_count} detection records",
        "deleted_count": deleted_count
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
