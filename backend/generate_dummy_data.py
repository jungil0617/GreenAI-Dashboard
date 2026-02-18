"""
더미 데이터 생성 스크립트

실시간 객체 감지 데이터를 시뮬레이션하여 /ingest 엔드포인트로 전송합니다.
"""

import requests
import random
import time
from datetime import datetime
import uuid


API_BASE_URL = "http://localhost:8000"


def generate_random_object():
    """랜덤 객체 데이터 생성"""
    object_types = ['Pedestrian', 'Bike', 'Vehicle', 'LargeVehicle']

    # 타입별 속도 범위 (m/s)
    speed_ranges = {
        'Pedestrian': (0.5, 2.0),      # 보행자: 1.8 ~ 7.2 km/h
        'Bike': (3.0, 8.0),             # 자전거: 10.8 ~ 28.8 km/h
        'Vehicle': (5.0, 15.0),         # 차량: 18 ~ 54 km/h
        'LargeVehicle': (4.0, 12.0)     # 대형차량: 14.4 ~ 43.2 km/h
    }

    obj_type = random.choice(object_types)
    speed_min, speed_max = speed_ranges[obj_type]

    return {
        "uuid": str(uuid.uuid4()),
        "type": obj_type,
        "x": round(random.uniform(0, 100), 2),
        "y": round(random.uniform(0, 100), 2),
        "speed_ms": round(random.uniform(speed_min, speed_max), 2)
    }


def generate_detection_data():
    """감지 데이터 생성"""
    zones = ['A구역', 'B구역', 'C구역']
    num_objects = random.randint(1, 5)  # 1~5개의 객체

    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "zone": random.choice(zones),
        "objects": [generate_random_object() for _ in range(num_objects)]
    }

    return data


def send_data(data):
    """데이터를 /ingest 엔드포인트로 전송"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/ingest",
            json=data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 201:
            print(f"✓ 전송 성공: {data['zone']}, {len(data['objects'])}개 객체")
            return True
        else:
            print(f"✗ 전송 실패: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 연결 실패: 백엔드 서버가 실행 중인지 확인하세요 (http://localhost:8000)")
        return False
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
        return False


def main():
    """메인 함수"""
    print("=== GreenAI Dashboard 더미 데이터 생성기 ===")
    print(f"대상 서버: {API_BASE_URL}")
    print("Ctrl+C로 중단할 수 있습니다.\n")

    # 서버 연결 확인
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"서버 상태: {response.json()}\n")
    except:
        print("경고: 서버에 연결할 수 없습니다. 계속 시도합니다...\n")

    interval = 3  # 3초 간격
    count = 0

    try:
        while True:
            data = generate_detection_data()
            if send_data(data):
                count += 1

            print(f"총 {count}건 전송 완료. {interval}초 후 다음 데이터 전송...\n")
            time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\n\n프로그램 종료. 총 {count}건의 데이터를 전송했습니다.")


def send_sample_data():
    """샘플 데이터 1건 전송"""
    sample_data = {
        "timestamp": "2026-02-12T14:30:00",
        "zone": "A구역",
        "objects": [
            {"uuid": "abc-123", "type": "Pedestrian", "x": 12.5, "y": 3.2, "speed_ms": 1.2},
            {"uuid": "def-456", "type": "Vehicle", "x": 45.1, "y": 8.7, "speed_ms": 8.3}
        ]
    }

    print("=== 샘플 데이터 전송 ===")
    print(f"데이터: {sample_data}\n")
    send_data(sample_data)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        send_sample_data()
    else:
        main()
