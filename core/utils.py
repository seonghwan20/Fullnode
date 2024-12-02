import json
import os

# 데이터 디렉토리 설정
DATA_DIR = "./data"

def ensure_data_directory():
    """
    데이터 디렉토리가 없으면 생성
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_json(filename):
    """
    JSON 파일을 읽어 Python 객체로 반환
    파일이 없거나 비어 있는 경우 기본값 {} 반환
    """
    filepath = os.path.join(DATA_DIR, filename)

    # 파일이 존재하지 않거나 비어 있을 경우 기본값 반환
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return {}

    with open(filepath, "r") as file:
        return json.load(file)

def write_json(filename, data):
    """
    Python 객체를 JSON 파일로 저장
    """
    filepath = os.path.join(DATA_DIR, filename)

    # 파일에 JSON 데이터 저장
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)
