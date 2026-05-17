"""
测试身份证号和国家识别功能
"""
from app.services.detection_engine import DetectionEngine


def test_id_card_detection():
    """测试身份证号识别"""
    engine = DetectionEngine()
    
    # 真实有效的身份证号（测试用，已脱敏）
    test_cases = [
        # 格式：(身份证号, 是否应该有效, 说明)
        ("110101199001011234", True, "北京东城区，1990年出生，男性"),
        ("110105198503152345", True, "北京朝阳区，1985年出生，女性"),
        ("310115199206153456", True, "上海浦东新区，1992年出生，男性"),
        ("440305198807204567", True, "深圳南山区，1988年出生，女性"),
        ("330106199512255678", True, "杭州西湖区，1995年出生，男性"),
        
        # 无效身份证号（校验位错误）
        ("110101199001011235", False, "校验位错误"),
        ("11010119900101123X", False, "校验位错误（应为数字）"),
        
        # 15位旧版身份证
        ("110101900101123", True, "15位旧版身份证"),
        
        # 明显无效的
        ("123456789012345678", False, "地区码和日期都无效"),
        ("000000000000000000", False, "全零，无效"),
    ]
    
    print("=" * 100)
    print("测试身份证号识别")
    print("=" * 100)
    
    for id_number, should_be_valid, description in test_cases:
        is_valid, confidence, metadata = engine.is_id_card(id_number)
        
        status = "✓" if is_valid == should_be_valid else "✗"
        print(f"\n{status} 身份证号: {id_number}")
        print(f"   说明: {description}")
        print(f"   识别结果: {'有效' if is_valid else '无效'} (置信度: {confidence:.2%})")
        
        if metadata:
            if 'area' in metadata:
                print(f"   地区: {metadata['area']}")
            if 'gender' in metadata:
                print(f"   性别: {metadata['gender']}")
            if 'age' in metadata:
                print(f"   年龄: {metadata['age']}岁")
            if 'birth_date' in metadata:
                print(f"   出生日期: {metadata['birth_date']}")
        
        if is_valid != should_be_valid:
            print(f"   ❌ 期望: {'有效' if should_be_valid else '无效'}, 实际: {'有效' if is_valid else '无效'}")


def test_country_detection():
    """测试国家名称识别"""
    engine = DetectionEngine()
    
    test_cases = [
        # 中文国家名
        ("中国", True),
        ("日本", True),
        ("美国", True),
        ("法国", True),
        ("德国", True),
        ("英国", True),
        ("韩国", True),
        ("俄罗斯", True),
        ("意大利", True),
        ("加拿大", True),
        ("澳大利亚", True),
        
        # 英文国家名
        ("China", True),
        ("Japan", True),
        ("United States", True),
        ("USA", True),
        ("France", True),
        ("Germany", True),
        ("United Kingdom", True),
        ("UK", True),
        ("Korea", True),
        
        # 不应该匹配的情况
        ("中国人", False),  # 包含国家名但不是纯国家名
        ("美国人", False),
        ("abc", False),
        ("123", False),
    ]
    
    print("\n" + "=" * 100)
    print("测试国家名称识别")
    print("=" * 100)
    
    for text, should_match in test_cases:
        matches = engine.scan_text(text)
        
        # 检查是否匹配到国家规则（ID=31）
        country_matches = [m for m in matches if m.rule_id == 31]
        matched = len(country_matches) > 0
        
        status = "✓" if matched == should_match else "✗"
        print(f"\n{status} 测试文本: '{text}'")
        
        if country_matches:
            for match in country_matches:
                print(f"   - 规则: {match.rule_name}")
                print(f"   - 置信度: {match.confidence:.2%}")
                print(f"   - 匹配内容: {match.matched_content}")
        else:
            print(f"   - 未检测到国家名称")
        
        if matched != should_match:
            print(f"   ❌ 期望: {'匹配' if should_match else '不匹配'}, 实际: {'匹配' if matched else '不匹配'}")


def test_mixed_content():
    """测试混合内容中的身份证和国家识别"""
    engine = DetectionEngine()
    
    print("\n" + "=" * 100)
    print("测试混合内容识别")
    print("=" * 100)
    
    test_texts = [
        "张三，110101199001011234，中国，13800138000",
        "李四，310115199206153456，上海市浦东新区，美国",
        "王五，440305198807204567，深圳南山区，日本",
    ]
    
    for text in test_texts:
        print(f"\n测试文本: {text}")
        matches = engine.scan_text(text)
        
        if matches:
            # 按置信度排序
            matches.sort(key=lambda m: m.confidence, reverse=True)
            for match in matches:
                rule_type = "身份证" if match.rule_id == 2 else \
                           "国家" if match.rule_id == 31 else \
                           "手机号" if match.rule_id == 1 else \
                           "地址" if match.rule_id == 5 else \
                           match.rule_name
                print(f"   - {rule_type}: {match.matched_content[:30]}... (置信度: {match.confidence:.2%})")
        else:
            print(f"   - 未检测到敏感信息")


if __name__ == "__main__":
    test_id_card_detection()
    test_country_detection()
    test_mixed_content()
    print("\n" + "=" * 100)
    print("测试完成")
    print("=" * 100)
