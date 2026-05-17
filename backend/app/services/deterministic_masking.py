"""
基于密钥分区的确定性数据脱敏引擎
Key-Partitioned Deterministic Data Masking Engine

核心原理：
1. 使用AES-256-ECB对原数据进行确定性加密
2. 对密文进行SHA256哈希，生成64位锚点
3. 使用SplitMix64 PRNG基于锚点生成确定性随机序列
4. 根据字段规则映射生成符合要求的脱敏数据

数学保证：
脱敏数据 = F(原数据, 密钥, 加密算法, 哈希算法, PRNG算法, 映射规则)
只要六个输入要素全部相同，输出结果必然相同。
"""

import hashlib
import struct
import secrets
from typing import Optional, Dict, Any


class SplitMix64Random:
    """SplitMix64 伪随机数生成器 - 确定性PRNG"""
    
    def __init__(self, seed: int):
        """
        使用锚点初始化
        Args:
            seed: 64位种子值（会自动转为无符号64位）
        """
        self.state = seed & 0xFFFFFFFFFFFFFFFF
    
    def next_int64(self) -> int:
        """生成下一个64位随机数"""
        self.state = (self.state + 0x9e3779b97f4a7c15) & 0xFFFFFFFFFFFFFFFF
        z = self.state
        z = ((z ^ (z >> 30)) * 0xbf58476d1ce4e5b9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94d049bb133111eb) & 0xFFFFFFFFFFFFFFFF
        return z ^ (z >> 31)
    
    def next_int(self, bound: int) -> int:
        """生成[0, bound)范围内的随机整数"""
        if bound <= 0:
            raise ValueError("Bound must be positive")
        r = self.next_int64() & 0x7FFFFFFFFFFFFFFF  # 确保为正数
        return r % bound
    
    def next_double(self, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """生成[min, max]范围内的随机浮点数"""
        r = self.next_int64() & 0x7FFFFFFFFFFFFFFF
        normalized = r / 0x7FFFFFFFFFFFFFFF
        return min_val + normalized * (max_val - min_val)
    
    def next_chars(self, chars: str, length: int) -> str:
        """从字符集中随机选择指定长度的字符串"""
        result = []
        for _ in range(length):
            idx = self.next_int(len(chars))
            result.append(chars[idx])
        return ''.join(result)


class DeterministicEncryptionEngine:
    """确定性加密引擎 - AES-256-ECB"""
    
    @staticmethod
    def encrypt(key_bytes: bytes, plaintext: str) -> bytes:
        """
        AES-256-ECB确定性加密
        Args:
            key_bytes: 32字节密钥（256位）
            plaintext: 原始数据
        Returns:
            密文字节
        """
        try:
            from Crypto.Cipher import AES
        except ImportError:
            # 如果没有pycryptodome，使用简化版（仅用于演示）
            return DeterministicEncryptionEngine._simple_encrypt(key_bytes, plaintext)
        
        # 确保密钥长度为32字节
        assert len(key_bytes) == 32, "Key must be 256 bits (32 bytes)"
        
        # 创建ECB模式加密器
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        
        # PKCS7填充
        plaintext_bytes = plaintext.encode('utf-8')
        pad_length = 16 - (len(plaintext_bytes) % 16)
        padded_plaintext = plaintext_bytes + bytes([pad_length] * pad_length)
        
        # 加密
        return cipher.encrypt(padded_plaintext)
    
    @staticmethod
    def _simple_encrypt(key_bytes: bytes, plaintext: str) -> bytes:
        """简化版加密（当没有pycryptodome时使用）"""
        # 使用HMAC-SHA256模拟确定性加密
        import hmac
        return hmac.new(key_bytes, plaintext.encode('utf-8'), hashlib.sha256).digest()
    
    @staticmethod
    def compute_anchor(ciphertext: bytes) -> int:
        """
        计算密文锚点
        Args:
            ciphertext: 密文字节
        Returns:
            64位整数锚点
        """
        # SHA-256哈希，取前8字节
        hash_bytes = hashlib.sha256(ciphertext).digest()[:8]
        
        # 转换为有符号64位整数（大端序）
        return struct.unpack('>q', hash_bytes)[0]


class FieldMapper:
    """字段映射器基类"""
    
    def generate(self, rng: SplitMix64Random, original_value: str, config: Dict[str, Any] = None) -> str:
        """
        生成脱敏数据
        Args:
            rng: 确定性的随机数生成器
            original_value: 原始数据
            config: 映射配置
        Returns:
            脱敏后的数据（必须不等于original_value）
        """
        raise NotImplementedError


class NameMapper(FieldMapper):
    """中文姓名映射器"""
    
    # 百家姓库（前100个常见姓氏）
    SURNAMES = [
        "赵", "钱", "孙", "李", "周", "吴", "郑", "王", "冯", "陈",
        "褚", "卫", "蒋", "沈", "韩", "杨", "朱", "秦", "尤", "许",
        "何", "吕", "施", "张", "孔", "曹", "严", "华", "金", "魏",
        "陶", "姜", "戚", "谢", "邹", "喻", "柏", "水", "窦", "章",
        "云", "苏", "潘", "葛", "奚", "范", "彭", "郎", "鲁", "韦",
        "昌", "马", "苗", "凤", "花", "方", "俞", "任", "袁", "柳",
        "酆", "鲍", "史", "唐", "费", "廉", "岑", "薛", "雷", "贺",
        "倪", "汤", "滕", "殷", "罗", "毕", "郝", "邬", "安", "常",
        "乐", "于", "时", "傅", "皮", "卞", "齐", "康", "伍", "余",
        "元", "卜", "顾", "孟", "平", "黄", "和", "穆", "萧", "尹"
    ]
    
    # 名字常用字库（500个）
    NAME_CHARS = [
        "伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军",
        "洋", "勇", "艳", "杰", "娟", "涛", "明", "超", "秀兰", "霞",
        "平", "辉", "玲", "桂", "凤", "英", "兰", "刚", "利", "萍",
        "青", "斌", "燕", "建", "国", "华", "梅", "林", "鑫", "丹",
        "峰", "波", "宁", "龙", "宇", "雷", "雪", "兵", "欢", "阳",
        "飞", "亮", "健", "俊", "鹏", "红", "晶", "慧", "晨", "颖"
    ]
    
    def generate(self, rng: SplitMix64Random, original_value: str, config: Dict[str, Any] = None) -> str:
        original_length = len(original_value)
        
        # 确定目标长度
        if original_length <= 2:
            target_length = 2
        elif original_length >= 4:
            target_length = 4
        else:
            target_length = 3
        
        # 循环生成，直到不等于原值
        max_attempts = 100
        for _ in range(max_attempts):
            # 选择姓氏
            surname = self.SURNAMES[rng.next_int(len(self.SURNAMES))]
            
            # 生成名字
            name_length = target_length - 1
            given_name = ""
            for _ in range(name_length):
                char_idx = rng.next_int(len(self.NAME_CHARS))
                given_name += self.NAME_CHARS[char_idx]
            
            result = surname + given_name
            
            # 确保不等于原值
            if result != original_value:
                return result
        
        # 如果100次都相同（极小概率），返回带后缀的结果
        return original_value + "某"


class PhoneMapper(FieldMapper):
    """手机号映射器"""
    
    def generate(self, rng: SplitMix64Random, original_value: str, config: Dict[str, Any] = None) -> str:
        # 中国大陆手机号格式：1XX XXXX XXXX
        prefixes = ["138", "139", "137", "136", "135", "134", "159", "158", "157", "150",
                   "151", "152", "188", "187", "182", "183", "184", "178", "198", "199"]
        
        max_attempts = 100
        for _ in range(max_attempts):
            prefix = prefixes[rng.next_int(len(prefixes))]
            middle = f"{rng.next_int(10000):04d}"
            suffix = f"{rng.next_int(10000):04d}"
            result = f"{prefix}{middle}{suffix}"
            
            if result != original_value:
                return result
        
        return "13800000000"


class IdCardMapper(FieldMapper):
    """身份证号映射器"""
    
    def generate(self, rng: SplitMix64Random, original_value: str, config: Dict[str, Any] = None) -> str:
        # 简化的身份证生成（实际应该更复杂，包含校验码）
        max_attempts = 100
        for _ in range(max_attempts):
            # 地区码（6位）
            area = f"{rng.next_int(900000) + 100000:06d}"
            # 生日（8位）
            year = rng.next_int(50) + 1970
            month = rng.next_int(12) + 1
            day = rng.next_int(28) + 1
            birthday = f"{year}{month:02d}{day:02d}"
            # 顺序码（3位）
            sequence = f"{rng.next_int(1000):03d}"
            # 校验码（1位，简化为0-9或X）
            check_chars = "0123456789X"
            check = check_chars[rng.next_int(11)]
            
            result = f"{area}{birthday}{sequence}{check}"
            
            if result != original_value:
                return result
        
        return "110101199001011234"


class EmailMapper(FieldMapper):
    """邮箱映射器"""
    
    DOMAINS = ["gmail.com", "qq.com", "163.com", "sina.com", "hotmail.com", "outlook.com"]
    CHARS = "abcdefghijklmnopqrstuvwxyz0123456789"
    
    def generate(self, rng: SplitMix64Random, original_value: str, config: Dict[str, Any] = None) -> str:
        max_attempts = 100
        for _ in range(max_attempts):
            # 生成用户名（6-12位）
            username_len = rng.next_int(7) + 6
            username = rng.next_chars(self.CHARS, username_len)
            
            # 选择域名
            domain = self.DOMAINS[rng.next_int(len(self.DOMAINS))]
            
            result = f"{username}@{domain}"
            
            if result != original_value:
                return result
        
        return "user@example.com"


class AddressMapper(FieldMapper):
    """地址映射器"""
    
    PROVINCES = ["北京市", "上海市", "广东省", "浙江省", "江苏省", "四川省", "湖北省", "湖南省"]
    CITIES = {
        "北京市": ["东城区", "西城区", "朝阳区", "海淀区"],
        "上海市": ["黄浦区", "徐汇区", "长宁区", "静安区"],
        "广东省": ["广州市", "深圳市", "珠海市", "佛山市"],
        "浙江省": ["杭州市", "宁波市", "温州市", "嘉兴市"],
    }
    STREETS = ["中山路", "人民路", "解放路", "建设路", "和平路", "胜利路"]
    
    def generate(self, rng: SplitMix64Random, original_value: str, config: Dict[str, Any] = None) -> str:
        province = self.PROVINCES[rng.next_int(len(self.PROVINCES))]
        cities = self.CITIES.get(province, ["市区"])
        city = cities[rng.next_int(len(cities))]
        street = self.STREETS[rng.next_int(len(self.STREETS))]
        number = rng.next_int(999) + 1
        
        result = f"{province}{city}{street}{number}号"
        
        if result != original_value:
            return result
        
        return "北京市朝阳区某某路1号"


class BankCardMapper(FieldMapper):
    """银行卡号映射器"""
    
    def generate(self, rng: SplitMix64Random, original_value: str, config: Dict[str, Any] = None) -> str:
        # 银联卡BIN码
        bins = ["622202", "622208", "622848", "621700", "623668"]
        
        max_attempts = 100
        for _ in range(max_attempts):
            bin_code = bins[rng.next_int(len(bins))]
            # 生成剩余10-13位
            remaining_len = 16 - len(bin_code)
            remaining = f"{rng.next_int(10 ** remaining_len):0{remaining_len}d}"
            result = bin_code + remaining
            
            if result != original_value:
                return result
        
        return "6222021234567890123"


class DeterministicMaskingEngine:
    """确定性脱敏引擎"""
    
    def __init__(self):
        self.encryption_engine = DeterministicEncryptionEngine()
        self.mappers: Dict[str, FieldMapper] = {
            'name': NameMapper(),
            'phone': PhoneMapper(),
            'id_card': IdCardMapper(),
            'email': EmailMapper(),
            'address': AddressMapper(),
            'bank_card': BankCardMapper(),
        }
    
    def mask(self, original_value: str, key_bytes: bytes, field_type: str, config: Dict[str, Any] = None) -> str:
        """
        执行确定性脱敏
        
        Args:
            original_value: 原始数据
            key_bytes: 32字节密钥
            field_type: 字段类型（name, phone, id_card, email, address, bank_card）
            config: 额外配置
        
        Returns:
            脱敏后的数据
        """
        if not original_value or original_value.strip() == "":
            return original_value
        
        # Step 1: 确定性加密
        ciphertext = self.encryption_engine.encrypt(key_bytes, original_value)
        
        # Step 2: 计算锚点
        anchor = self.encryption_engine.compute_anchor(ciphertext)
        
        # Step 3: 初始化PRNG
        rng = SplitMix64Random(anchor)
        
        # Step 4: 字段规则映射
        mapper = self.mappers.get(field_type)
        if not mapper:
            # 默认使用通用遮盖
            return "*" * len(original_value)
        
        result = mapper.generate(rng, original_value, config)
        
        # 最终检查：确保不等于原值
        if result == original_value:
            # 极端情况下，添加后缀
            return result + "_masked"
        
        return result
    
    def generate_key(self) -> bytes:
        """生成新的256位密钥"""
        return secrets.token_bytes(32)


# 测试代码
if __name__ == "__main__":
    engine = DeterministicMaskingEngine()
    
    # 生成密钥
    key = engine.generate_key()
    print(f"密钥（Base64）: {key.hex()}")
    print()
    
    # 测试确定性
    test_cases = [
        ("张三", "name"),
        ("13800138000", "phone"),
        ("110101199001011234", "id_card"),
        ("test@gmail.com", "email"),
    ]
    
    print("=" * 60)
    print("测试1: 相同密钥下的确定性")
    print("=" * 60)
    for value, field_type in test_cases:
        result1 = engine.mask(value, key, field_type)
        result2 = engine.mask(value, key, field_type)
        print(f"{field_type:10s}: {value:20s} -> {result1:20s} (重复: {result1 == result2})")
    
    print()
    print("=" * 60)
    print("测试2: 不同密钥下的隔离性")
    print("=" * 60)
    key2 = engine.generate_key()
    for value, field_type in test_cases:
        result1 = engine.mask(value, key, field_type)
        result2 = engine.mask(value, key2, field_type)
        print(f"{field_type:10s}: 密钥1={result1:20s} | 密钥2={result2:20s} (不同: {result1 != result2})")
