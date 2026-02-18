from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base


class Detection(Base):
    """
    객체 감지 데이터 모델

    각 객체마다 하나의 레코드가 생성됩니다.
    샘플 데이터의 objects 배열 내 각 항목이 하나의 Detection으로 저장됩니다.
    """
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)  # 감지 시각
    zone = Column(String, nullable=False, index=True)  # 구역 (예: "A구역")
    uuid = Column(String, nullable=False, index=True)  # 객체 고유 ID
    object_type = Column(String, nullable=False, index=True)  # 'Pedestrian', 'Bike', 'Vehicle', 'LargeVehicle'
    x = Column(Float, nullable=False)  # x 좌표
    y = Column(Float, nullable=False)  # y 좌표
    speed_ms = Column(Float, nullable=True)  # 속도 (m/s 단위)

    def __repr__(self):
        return f"<Detection(id={self.id}, uuid={self.uuid}, type={self.object_type}, zone={self.zone}, timestamp={self.timestamp})>"
