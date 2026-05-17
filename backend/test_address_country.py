"""
测试地址和国家识别功能
"""
from app.services.detection_engine import DetectionEngine

def test_country_detection():
    """测试国家名称识别"""
    engine = DetectionEngine()
    
    test_cases = [
        # 中文国家名
        ("中国", True, "国家名称"),
        ("日本", True, "国家名称"),
        ("美国", True, "国家名称"),
        ("法国", True, "国家名称"),
        ("德国", True, "国家名称"),
        ("英国", True, "国家名称"),
        ("韩国", True, "国家名称"),
        
        # 英文国家名
        ("China", True, "国家名称"),
        ("Japan", True, "国家名称"),
        ("United States", True, "国家名称"),
        ("France", True, "国家名称"),
        ("Germany", True, "国家名称"),
        ("United Kingdom", True, "国家名称"),
        ("Korea", True, "国家名称"),
    ]
    
    print("=" * 80)
    print("测试国家名称识别")
    print("=" * 80)
    
    for text, should_match, expected_rule in test_cases:
        matches = engine.scan_text(text)
        matched = len(matches) > 0
        
        status = "✓" if matched == should_match else "✗"
        print(f"\n{status} 测试文本: {text}")
        
        if matches:
            for match in matches:
                print(f"   - 规则ID: {match.rule_id}, 规则名: {match.rule_name}")
                print(f"   - 置信度: {match.confidence}")
                print(f"   - 匹配内容: {match.matched_content}")
        else:
            print(f"   - 未检测到任何规则")
        
        if matched != should_match:
            print(f"   ❌ 期望: {'匹配' if should_match else '不匹配'}, 实际: {'匹配' if matched else '不匹配'}")


def test_address_detection():
    """测试地址识别"""
    engine = DetectionEngine()
    
    test_cases = [
        # 中文地址（应该匹配：多个关键词或数字+关键词）
        ("北京市海淀区中关村大街1号", True, "中文地址关键词"),
        ("上海市浦东新区陆家嘴环路1000号", True, "中文地址关键词"),
        ("广东省深圳市南山区科技路88号", True, "中文地址关键词"),
        ("北京市朝阳区建国路93号万达广场", True, "中文地址关键词"),
        
        # 单个关键词但无数字（可能不匹配）
        ("北京市", False, "需要更多上下文"),
        ("街道", False, "太短"),
        
        # 英文地址
        ("123 Main Street", True, "英文地址关键词"),
        ("456 Oak Avenue Apt 789", True, "英文地址关键词"),
        ("789 Park Road", True, "英文地址关键词"),
        
        # 日文地址
        ("東京都渋谷区神宮前1丁目2番3号", True, "日文地址关键词"),
        ("大阪府大阪市北区梅田3丁目", True, "日文地址关键词"),
    ]
    
    print("\n" + "=" * 80)
    print("测试地址识别")
    print("=" * 80)
    
    for text, should_match, note in test_cases:
        matches = engine.scan_text(text)
        matched = len(matches) > 0
        
        status = "✓" if matched == should_match else "✗"
        print(f"\n{status} 测试文本: {text}")
        print(f"   备注: {note}")
        
        if matches:
            for match in matches:
                print(f"   - 规则ID: {match.rule_id}, 规则名: {match.rule_name}")
                print(f"   - 置信度: {match.confidence}")
                print(f"   - 匹配内容: {match.matched_content[:50]}...")
        else:
            print(f"   - 未检测到任何规则")


def test_mixed_content():
    """测试混合内容识别"""
    engine = DetectionEngine()
    
    print("\n" + "=" * 80)
    print("测试混合内容识别")
    print("=" * 80)
    
    test_texts = [
        "张三，中国，13800138000",
        "John Smith, United States, john@example.com",
        "田中太郎，日本，090-1234-5678",
    ]
    
    for text in test_texts:
        print(f"\n测试文本: {text}")
        matches = engine.scan_text(text)
        
        if matches:
            for match in matches:
                print(f"   - {match.rule_name} (置信度: {match.confidence})")
        else:
            print(f"   - 未检测到敏感信息")


if __name__ == "__main__":
    test_country_detection()
    test_address_detection()
    test_mixed_content()
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
