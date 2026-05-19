"""
地址识别测试脚本
基于真实测试数据的多语言地址识别功能测试
"""
import sys
sys.path.insert(0, '../backend')

from app.services.address_parser import AddressIdentifier

# 基于真实测试数据的用例
test_cases = [
    # ==================== 中文地址 ====================
    ("广西壮族自治区沈阳县友好虞路x座 917806", "address", "中国地址（含座+邮编）"),
    ("西藏自治区南京县兴山淮安街d座 299802", "address", "中国地址（含座+邮编）"),
    ("福建省荆门市友好潜江路p座 182820", "address", "中国地址"),
    ("江西省萍乡市安源区建设西路88号 134776", "address", "中国地址"),
    
    # ==================== 韩文地址 ====================
    ("대전 광역시 송파구 언주65가 937-79", "address", "韩国地址（광역시+구）"),
    ("인천 광역시 동구 신포동 668451", "address", "韩国地址（광역시+구+동）"),
    ("세종특별자치시 소규모 937-79", "address", "韩国地址（特别自治市）"),
    
    # ==================== 日文地址 ====================
    ("長崎県横浜市港南区白金台31丁目18番17号", "address", "日本地址（県+市+区+丁目+番+号）"),
    ("神奈川県横浜市港南区上大岡西1丁目3-1", "address", "日本地址"),
    ("埼玉県川口市栄町3丁目18番17号", "address", "日本地址（埼玉県）"),
    
    # ==================== 英文地址 ====================
    ("72658 Braun Springs, Forbesview, NY 94223", "address", "美国地址（州缩写+邮编）"),
    ("5917 Sarah Mission Suite 406, Richardsberg, MH 54026", "address", "美国地址（Suite+州缩写）"),
    ("Flat 9, Lewis Club, East Alexandraburgh, WV55 4BH", "address", "英国地址"),
    ("Flat 7, Hawkins Locks, South Aimeeland, CV1H 1FX", "address", "英国地址"),
    
    # ==================== 德文地址 ====================
    ("Bettina-Hermann-Straße 257, 95961 Eichstätt", "address", "德国地址（-Straße模式）"),
    ("Hans-Günter-Preiß-Weg 600, 05626 Wolgast", "address", "德国地址（-Weg模式）"),
    ("Meisterstr. 7, 00251 Delitzsch", "address", "德国地址（Str.缩写）"),
    
    # ==================== 法文地址 ====================
    ("241, boulevard Victoire Da Silva, 66808 Benoit", "address", "法国地址（boulevard）"),
    ("8, chemin de Sanchez, 33330 Ledoux", "address", "法国地址（chemin）"),
    
    # ==================== 中文姓名（不应识别为地址） ====================
    ("薛慧", "name", "中文姓名"),
    ("冯杰秀英", "name", "中文姓名（4字）"),
    ("许娜", "name", "中文姓名"),
    ("郑杰静", "name", "中文姓名"),
    
    # ==================== 英文姓名（不应识别为地址） ====================
    ("Wanda Bell", "name", "英文姓名"),
    ("Martin Blot", "name", "英文姓名"),
    ("Linda Johnson", "name", "英文姓名"),
    ("Ernest Monroe", "name", "英文姓名"),
    ("Vincent Lamy", "name", "法文姓名"),
    ("Anto Jungfer", "name", "德文姓名"),
    
    # ==================== 韩文姓名（不应识别为地址） ====================
    ("이 경 자", "name", "韩文姓名（3个词）"),
    ("안 태 진", "name", "韩文姓名"),
    ("임철수철수", "name", "韩文姓名（无空格）"),
    
    # ==================== 日文姓名（不应识别为地址） ====================
    ("小川 香香", "name", "日文姓名"),
    ("吉田 拓真", "name", "日文姓名"),
    ("田中太郎", "name", "日文姓名（无空格）"),
]

print("=" * 80)
print("地址识别测试（基于真实测试数据）")
print("=" * 80)

correct = 0
total = len(test_cases)

for text, expected_type, description in test_cases:
    is_addr, confidence, reason, address_info = AddressIdentifier.is_address(text)
    
    # 判断是否正确
    if expected_type == "address":
        is_correct = is_addr and confidence >= 0.25
    else:
        is_correct = not is_addr or confidence < 0.25
    
    if is_correct:
        correct += 1
        status = "✅"
    else:
        status = "❌"
    
    print(f"\n{status} {description}")
    print(f"   文本: {text}")
    print(f"   结果: {'地址' if is_addr else '非地址'}, 置信度: {confidence:.2f}")
    print(f"   理由: {reason}")
    if address_info:
        parts = []
        if address_info.province: parts.append(f"省={address_info.province}")
        if address_info.city: parts.append(f"市={address_info.city}")
        if address_info.district: parts.append(f"区={address_info.district}")
        if parts:
            print(f"   解析: {', '.join(parts)}")

print("\n" + "=" * 80)
print(f"测试结果: {correct}/{total} 正确 ({correct/total*100:.1f}%)")

# 分组统计
addr_tests = [(t, d) for t, d, _ in test_cases if d == "address"]
name_tests = [(t, d) for t, d, _ in test_cases if d == "name"]

addr_correct = sum(1 for t, _ in addr_tests if AddressIdentifier.is_address(t)[0] and AddressIdentifier.is_address(t)[1] >= 0.25)
name_correct = sum(1 for t, _ in name_tests if not AddressIdentifier.is_address(t)[0] or AddressIdentifier.is_address(t)[1] < 0.25)

print(f"\n地址识别: {addr_correct}/{len(addr_tests)} 正确 ({addr_correct/len(addr_tests)*100:.1f}%)")
print(f"姓名排除: {name_correct}/{len(name_tests)} 正确 ({name_correct/len(name_tests)*100:.1f}%)")
print("=" * 80)
