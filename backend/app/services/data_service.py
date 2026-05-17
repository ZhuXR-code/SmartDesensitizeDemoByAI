import os
import io
import csv
import json
import chardet
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class DataService:
    SUPPORTED_FORMATS = {
        "csv": ["csv"],
        "excel": ["xlsx", "xls"],
        "text": ["txt", "md", "log"],
        "json": ["json"]
    }
    
    @classmethod
    def detect_encoding(cls, file_path: str) -> str:
        with open(file_path, "rb") as f:
            raw_data = f.read(100000)
            result = chardet.detect(raw_data)
            detected = result.get("encoding", "utf-8") or "utf-8"
            if detected.lower() == "gb2312":
                return "gbk"
            return detected
    
    @classmethod
    def read_file(cls, file_path: str, file_format: Optional[str] = None, 
                  encoding: Optional[str] = None) -> pd.DataFrame:
        path = Path(file_path)
        ext = (file_format or path.suffix.lower().lstrip("."))
        
        if not encoding:
            encoding = cls.detect_encoding(file_path)
        
        if ext in cls.SUPPORTED_FORMATS["csv"]:
            try:
                return pd.read_csv(file_path, encoding=encoding)
            except UnicodeDecodeError:
                for enc in ["utf-8", "gbk", "gb2312", "gb18030", "latin1"]:
                    try:
                        return pd.read_csv(file_path, encoding=enc)
                    except:
                        continue
                raise
        elif ext in cls.SUPPORTED_FORMATS["excel"]:
            return pd.read_excel(file_path)
        elif ext in cls.SUPPORTED_FORMATS["text"]:
            with open(file_path, "r", encoding=encoding) as f:
                lines = f.readlines()
            df = pd.DataFrame({"content": [line.strip() for line in lines]})
            return df
        elif ext in cls.SUPPORTED_FORMATS["json"]:
            with open(file_path, "r", encoding=encoding) as f:
                data = json.load(f)
            if isinstance(data, list):
                return pd.DataFrame(data)
            else:
                return pd.DataFrame([data])
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
    
    @classmethod
    def read_from_text(cls, text: str, format_type: str = "csv") -> pd.DataFrame:
        if format_type == "csv":
            return pd.read_csv(io.StringIO(text))
        elif format_type == "json":
            data = json.loads(text)
            if isinstance(data, list):
                return pd.DataFrame(data)
            return pd.DataFrame([data])
        else:
            lines = text.strip().split("\n")
            return pd.DataFrame({"content": lines})
    
    @classmethod
    def save_to_file(cls, df: pd.DataFrame, file_path: str, file_format: str = "csv",
                     encoding: str = "utf-8") -> str:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if file_format in cls.SUPPORTED_FORMATS["csv"]:
            df.to_csv(file_path, index=False, encoding=encoding or "utf-8-sig")
        elif file_format in cls.SUPPORTED_FORMATS["excel"]:
            df.to_excel(file_path, index=False)
        elif file_format in cls.SUPPORTED_FORMATS["json"]:
            df.to_json(file_path, orient="records", force_ascii=False)
        else:
            with open(file_path, "w", encoding=encoding) as f:
                for _, row in df.iterrows():
                    f.write(str(row.iloc[0]) + "\n")
        
        return file_path
    
    @classmethod
    def get_file_info(cls, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        stat = path.stat()
        
        try:
            df = cls.read_file(file_path)
            return {
                "file_name": path.name,
                "file_size": stat.st_size,
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns),
                "preview": df.head(5).to_dict("records")
            }
        except Exception as e:
            return {
                "file_name": path.name,
                "file_size": stat.st_size,
                "error": str(e)
            }
    
    @classmethod
    def generate_temp_filename(cls, original_name: str, suffix: str = "") -> str:
        import time
        timestamp = int(time.time())
        name = Path(original_name).stem
        ext = Path(original_name).suffix
        if suffix:
            return f"{name}_{suffix}_{timestamp}{ext}"
        return f"{name}_temp_{timestamp}{ext}"
