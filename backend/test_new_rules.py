"""测试新的脱敏规则函数"""
from app.services.desensitization_engine import DesensitizationEngine

def test_desensitization_rules():
    engine = DesensitizationEngine()
    
    print("=" * 80)
    print("测试脱敏规则函数")
    print("=" * 80)
    
    # 测试完全遮盖
    print("\n【完全遮盖】")
    result = engine.desensitize("张三", 1)  # 完全遮盖 rule_id=1
    print(f"  原始: 张三 -> 脱敏: {result}")
    assert result == "*", f"期望 '*', 实际 '{result}'"
    print("  ✓ 完全遮盖测试通过")
    
    # 测试仿真造数
    print("\n【仿真造数】")
    
    # 姓名仿真
    result = engine.desensitize("张三", 2)  # 姓名仿真 rule_id=2
    print(f"  姓名仿真: 张三 -> {result}")
    assert len(result) >= 2 and all('\u4e00' <= c <= '\u9fff' for c in result), "应为中文姓名"
    print("  ✓ 姓名仿真测试通过")
    
    # 手机号仿真
    result = engine.desensitize("13800138000", 3)  # 手机号仿真 rule_id=3
    print(f"  手机号仿真: 13800138000 -> {result}")
    assert len(result) == 11 and result.startswith("1"), "应为11位手机号"
    print("  ✓ 手机号仿真测试通过")
    
    # 身份证号仿真
    result = engine.desensitize("110101199001011234", 4)  # 身份证仿真 rule_id=4
    print(f"  身份证仿真: 110101199001011234 -> {result}")
    assert len(result) == 18, "应为18位身份证号"
    print("  ✓ 身份证号仿真测试通过")
    
    # 银行卡号仿真
    result = engine.desensitize("6222021234567890123", 5)  # 银行卡仿真 rule_id=5
    print(f"  银行卡仿真: 6222021234567890123 -> {result}")
    assert len(result) >= 16, "应为银行卡号"
    print("  ✓ 银行卡号仿真测试通过")
    
    # 地址仿真
    result = engine.desensitize("北京市海淀区中关村大街1号", 6)  # 地址仿真 rule_id=6
    print(f"  地址仿真: 北京市海淀区中关村大街1号 -> {result}")
    assert "省" in result or "市" in result, "应包含省市信息"
    print("  ✓ 地址仿真测试通过")
    
    # 国家仿真
    result = engine.desensitize("中国", 7)  # 国家仿真 rule_id=7
    print(f"  国家仿真: 中国 -> {result}")
    assert result in engine.COUNTRIES, "应为有效国家名称"
    print("  ✓ 国家仿真测试通过")
    
    # 测试部分遮盖
    print("\n【部分遮盖】")
    
    # 姓名部分遮盖
    result = engine.desensitize("张三", 13)  # 姓名部分遮盖 rule_id=13
    print(f"  姓名部分遮盖: 张三 -> {result}")
    assert result.startswith("张") and "*" in result, "应保留姓氏"
    print("  ✓ 姓名部分遮盖测试通过")
    
    # 手机号部分遮盖
    result = engine.desensitize("13800138000", 14)  # 手机号部分遮盖 rule_id=14
    print(f"  手机号部分遮盖: 13800138000 -> {result}")
    assert result.startswith("138") and result.endswith("8000"), "应保留前3后4位"
    print("  ✓ 手机号部分遮盖测试通过")
    
    # 身份证部分遮盖
    result = engine.desensitize("110101199001011234", 15)  # 身份证部分遮盖 rule_id=15
    print(f"  身份证部分遮盖: 110101199001011234 -> {result}")
    assert result.startswith("110") and result.endswith("1234"), "应保留前3后4位"
    print("  ✓ 身份证部分遮盖测试通过")
    
    # 银行卡部分遮盖
    result = engine.desensitize("6222021234567890123", 16)  # 银行卡部分遮盖 rule_id=16
    print(f"  银行卡部分遮盖: 6222021234567890123 -> {result}")
    assert result.startswith("6222") and result.endswith("0123"), "应保留前4后4位"
    print("  ✓ 银行卡部分遮盖测试通过")
    
    # 地址部分遮盖
    result = engine.desensitize("北京市海淀区中关村大街1号", 17)  # 地址部分遮盖 rule_id=17
    print(f"  地址部分遮盖: 北京市海淀区中关村大街1号 -> {result}")
    assert result.startswith("北京市海"), "应保留前6个字符"
    print("  ✓ 地址部分遮盖测试通过")
    
    # 国家部分遮盖
    result = engine.desensitize("中国", 18)  # 国家部分遮盖 rule_id=18
    print(f"  国家部分遮盖: 中国 -> {result}")
    assert result.startswith("中") and result.endswith("国"), "应保留首尾"
    print("  ✓ 国家部分遮盖测试通过")
    
    print("\n" + "=" * 80)
    print("✅ 所有测试通过！")
    print("=" * 80)

if __name__ == "__main__":
    test_desensitization_rules()
