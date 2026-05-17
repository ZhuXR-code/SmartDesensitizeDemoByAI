import requests
import json
import pandas as pd
import os

BASE_URL = "http://localhost:8000"

def init_data():
    # 读取测试数据
    df = pd.read_csv("../test_data/sample_sensitive_data.csv", encoding="utf-8")
    
    # 保存为临时文件用于上传
    temp_path = "../uploads/test_data_utf8.csv"
    os.makedirs("../uploads", exist_ok=True)
    df.to_csv(temp_path, index=False, encoding="utf-8")
    
    # 上传文件
    with open(temp_path, "rb") as f:
        files = {"file": ("test_data.csv", f, "text/csv")}
        data = {"name": "多语言敏感数据测试集", "encoding": "utf-8"}
        resp = requests.post(f"{BASE_URL}/api/datasets/upload", files=files, data=data)
        print("Upload response:", resp.json())
    
    # 获取数据集列表
    resp = requests.get(f"{BASE_URL}/api/datasets/list")
    datasets = resp.json()["data"]["items"]
    print(f"Datasets: {len(datasets)}")
    
    if datasets:
        dataset_id = datasets[0]["id"]
        
        # 创建识别任务
        task_data = {
            "name": "测试识别任务",
            "dataset_id": dataset_id,
            "language_strategy": "auto"
        }
        resp = requests.post(f"{BASE_URL}/api/detection/tasks", json=task_data)
        print("Detection task:", resp.json())
        
        # 获取密钥列表
        resp = requests.get(f"{BASE_URL}/api/desensitization/keys")
        keys = resp.json()["data"]
        print(f"Keys: {len(keys)}")

if __name__ == "__main__":
    init_data()
