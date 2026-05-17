"""
测试地址解析功能（增强版）
"""
from app.services.address_parser import AddressParser, AddressInfo, AddressIdentifier


def test_address_parsing():
    """测试地址解析"""
    
    test_cases = [
        # 完整地址
        ("北京市海淀区中关村大街1号", "完整地址，包含省市区街道"),
        ("上海市浦东新区陆家嘴环路1000号", "完整地址，直辖市"),
        ("广东省深圳市南山区科技路88号", "完整地址，省份+城市"),
        ("浙江省杭州市西湖区文三路100号", "完整地址"),
        
        # 省市地址
        ("北京市", "只有直辖市"),
        ("上海市浦东新区", "直辖市+区"),
        ("广东省广州市", "省份+城市"),
        ("浙江省杭州市西湖区", "省份+城市+区"),
        
        # 详细地址
        ("中关村大街1号", "只有街道和门牌号"),
        ("文三路100号3号楼501室", "街道+门牌+楼栋+房间"),
        ("建国路93号万达广场A座", "街道+门牌+建筑"),
        
        # 农村地址
        ("河北省石家庄市鹿泉区李村镇南庄村", "农村地址"),
        ("湖南省长沙市长沙县跳马镇石燕湖村", "农村地址"),
        
        # 带邮编和电话
        ("北京市朝阳区建国路93号 100020 电话:13800138000", "带邮编和电话"),
        
        # 不应该匹配的情况
        ("abc", "英文，不是地址"),
        ("123", "纯数字"),
        ("张三", "人名"),
    ]
    
    print("=" * 100)
    print("测试地址解析功能")
    print("=" * 100)
    
    for address, description in test_cases:
        print(f"\n测试地址: {address}")
        print(f"说明: {description}")
        
        is_addr, confidence, reason, addr_info = AddressIdentifier.is_address(address)
        
        print(f"识别结果: {'✓ 是地址' if is_addr else '✗ 不是地址'} (置信度: {confidence:.2%})")
        print(f"理由: {reason}")
        
        if addr_info:
            print(f"  省份: {addr_info.province or 'N/A'}")
            print(f"  城市: {addr_info.city or 'N/A'}")
            print(f"  区县: {addr_info.district or 'N/A'}")
            print(f"  街道: {addr_info.street or 'N/A'}")
            print(f"  社区: {addr_info.community or 'N/A'}")
            print(f"  建筑: {addr_info.building or 'N/A'}")
            print(f"  房间: {addr_info.room or 'N/A'}")
            print(f"  邮编: {addr_info.postal_code or 'N/A'}")
            print(f"  电话: {addr_info.phone or 'N/A'}")
            print(f"  地址类型: {addr_info.address_type.value}")
            print(f"  解析级别: {addr_info.parsed_level.value}")


def test_detection_engine_integration():
    """测试与检测引擎的集成"""
    from app.services.detection_engine import DetectionEngine
    
    print("\n" + "=" * 100)
    print("测试检测引擎中的地址识别")
    print("=" * 100)
    
    engine = DetectionEngine()
    
    test_addresses = [
        "北京市海淀区中关村大街1号",
        "上海市浦东新区陆家嘴环路1000号",
        "广东省深圳市南山区科技路88号",
        "北京市",  # 应该不匹配（层级太少）
        "abc",     # 应该不匹配
    ]
    
    for address in test_addresses:
        print(f"\n测试文本: {address}")
        matches = engine.scan_text(address)
        
        # 查找地址规则的匹配
        address_matches = [m for m in matches if m.rule_id == 5]
        
        if address_matches:
            for match in address_matches:
                print(f"  ✓ 规则: {match.rule_name}")
                print(f"  置信度: {match.confidence:.2%}")
                print(f"  匹配内容: {match.matched_content[:50]}...")
        else:
            print(f"  ✗ 未检测到地址")


if __name__ == "__main__":
    test_address_parsing()
    test_detection_engine_integration()
    print("\n" + "=" * 100)
    print("测试完成")
    print("=" * 100)
