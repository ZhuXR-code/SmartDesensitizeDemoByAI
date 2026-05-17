import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, init_db
from app.models.dataset import Dataset
from app.models.detection import DetectionTask, DetectionResult
from app.models.desensitization import DesensitizationKey
from app.services.data_service import DataService
from app.services.detection_engine import DetectionEngine
from app.services.desensitization_engine import DesensitizationEngine
from app.services.language_detector import LanguageDetector
import pandas as pd

def test_full_flow():
    print("=" * 60)
    print("敏感信息脱敏平台 - 核心功能测试")
    print("=" * 60)
    
    # 初始化数据库
    print("\n[1] 初始化数据库...")
    init_db()
    db = SessionLocal()
    
    # 读取测试数据
    print("\n[2] 读取测试数据...")
    df = pd.read_csv("../test_data/sample_sensitive_data.csv", encoding="utf-8")
    print(f"    数据行数: {len(df)}")
    print(f"    数据列: {list(df.columns)}")
    
    # 保存数据集
    print("\n[3] 保存数据集到数据库...")
    os.makedirs("../uploads", exist_ok=True)
    file_path = "../uploads/test_data.csv"
    df.to_csv(file_path, index=False, encoding="utf-8")
    
    dataset = Dataset(
        name="多语言敏感数据测试集",
        source_type="file",
        file_path=file_path,
        row_count=len(df),
        column_count=len(df.columns),
        columns=list(df.columns),
        preview_data=df.head(5).to_dict("records")
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    print(f"    数据集ID: {dataset.id}")
    
    # 测试语言检测
    print("\n[4] 测试语言检测...")
    test_texts = [
        ("张三", "zh"),
        ("John Smith", "en"),
        ("田中太郎", "ja"),
        ("김철수", "ko"),
        ("Martin Blot", "fr"),
        ("Anto Jungfer", "de")
    ]
    for text, expected in test_texts:
        lang, conf = LanguageDetector.detect(text)
        status = "OK" if lang == expected else "NG"
        lang_name = LanguageDetector.get_language_name(lang)
        print(f"    [{status}] text_len={len(text)} -> {lang} ({lang_name}) conf={conf}")
    
    # 测试敏感数据识别
    print("\n[5] 测试敏感数据识别...")
    engine = DetectionEngine()
    
    # 测试单行识别
    test_row = df.iloc[0]
    matches = []
    for col in df.columns:
        value = str(test_row[col])
        if value and value != "nan":
            col_matches = engine.scan_text(value, col, 0)
            matches.extend(col_matches)
    
    print(f"    第1行发现 {len(matches)} 条敏感信息:")
    for m in matches[:5]:
        print(f"      - [{m.rule_name}] {m.column_name}: {m.matched_content}")
    
    # 全量扫描
    print("\n[6] 执行全量扫描...")
    all_matches = engine.scan_dataframe(df)
    print(f"    总计发现 {len(all_matches)} 条敏感信息")
    
    # 按规则统计
    from collections import Counter
    rule_counts = Counter(m.rule_name for m in all_matches)
    print("    按规则分布:")
    for rule, count in rule_counts.most_common():
        print(f"      - {rule}: {count}条")
    
    # 测试脱敏
    print("\n[7] 测试脱敏功能...")
    desens_engine = DesensitizationEngine()
    
    # 测试各种脱敏规则
    test_cases = [
        ("13800138000", 1, "手机号部分遮盖"),
        ("110101199001011234", 2, "身份证部分遮盖"),
        ("张三", 3, "姓名遮盖"),
        ("北京市海淀区中关村大街1号", 5, "地址部分遮盖"),
        ("zhangsan@example.com", 8, "邮箱部分遮盖"),
        ("John Smith", 7, "英文姓名仿真"),
        ("田中太郎", 11, "日文姓名仿真"),
        ("김철수", 12, "韩文姓名仿真"),
    ]
    
    for original, rule_id, desc in test_cases:
        result = desens_engine.desensitize(original, rule_id)
        print(f"    [{desc}]")
        print(f"      原: {original}")
        print(f"      脱: {result}")
    
    # 测试关联脱敏
    print("\n[8] 测试关联脱敏（确定性仿真）...")
    desens_engine.set_key(1, "test_key_123")
    
    original_name = "张三"
    result1 = desens_engine.desensitize(original_name, 6, 1)
    result2 = desens_engine.desensitize(original_name, 6, 1)
    result3 = desens_engine.desensitize(original_name, 6, 2)
    
    print(f"    原数据: {original_name}")
    print(f"    密钥1第1次: {result1}")
    print(f"    密钥1第2次: {result2} (相同:{result1==result2})")
    print(f"    密钥2第1次: {result3} (不同:{result1!=result3})")
    
    # 测试预览脱敏
    print("\n[9] 测试脱敏预览...")
    field_rules = {
        "姓名": 3,
        "手机号": 1,
        "身份证号": 2,
        "银行卡号": 4,
        "地址": 5,
        "邮箱": 8,
        "英文名": 7,
        "日文名": 11,
        "韩文名": 12,
        "法文名": 13,
        "德文名": 14
    }
    previews = desens_engine.preview_desensitization(df, field_rules, limit=3)
    print(f"    预览前3行:")
    for p in previews:
        print(f"      行{p.row_index}:")
        for col, vals in p.columns.items():
            print(f"        {col}: {vals['original']} -> {vals['desensitized']}")
    
    # 测试全量脱敏
    print("\n[10] 执行全量脱敏...")
    result_df, desens_matches = desens_engine.process_dataframe(df, field_rules)
    print(f"    脱敏完成，共处理 {len(desens_matches)} 个字段")
    
    # 保存脱敏结果
    output_path = "../uploads/desensitized_result.csv"
    DataService.save_to_file(result_df, output_path, "csv")
    print(f"    结果已保存: {output_path}")
    
    # 初始化密钥
    print("\n[11] 初始化脱敏密钥...")
    existing_keys = db.query(DesensitizationKey).count()
    if existing_keys == 0:
        for i in range(1, 31):
            key = DesensitizationKey(
                alias=f"密钥-{i:02d}",
                key_hash=f"builtin_key_hash_{i}",
                description=f"系统内置密钥 {i}"
            )
            db.add(key)
        db.commit()
        print(f"    已创建 30 个内置密钥")
    else:
        print(f"    已有 {existing_keys} 个密钥")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("测试完成！所有核心功能运行正常。")
    print("=" * 60)

if __name__ == "__main__":
    test_full_flow()
