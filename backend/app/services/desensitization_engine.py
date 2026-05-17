import re
import hashlib
import random
import string
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from app.services.language_detector import LanguageDetector


@dataclass
class DesensitizationMatch:
    row_index: int
    column_name: str
    original_value: str
    desensitized_value: str
    rule_id: int
    rule_name: str


class DesensitizationEngine:
    BUILTIN_RULES = [
        # ========== 完全遮盖 ==========
        {
            "id": 1, "name": "完全遮盖", "language": "all", 
            "desensitization_method": "full_mask",
            "category": "mask",
            "method": "full_mask", 
            "config": {"mask_char": "*"},
            "description": "将原始数据完全替换为单个*号",
            "example": {"before": "张三", "after": "*"}
        },
        
        # ========== 仿真造数 ==========
        {
            "id": 2, "name": "姓名仿真", "language": "zh",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_chinese_name", 
            "config": {},
            "description": "生成随机的中文姓名",
            "example": {"before": "张三", "after": "李伟"}
        },
        {
            "id": 3, "name": "手机号仿真", "language": "zh",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_chinese_phone", 
            "config": {},
            "description": "生成随机的中国手机号",
            "example": {"before": "13800138000", "after": "13912345678"}
        },
        {
            "id": 4, "name": "身份证号仿真", "language": "zh",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_chinese_id", 
            "config": {},
            "description": "生成随机的中国身份证号",
            "example": {"before": "110101199001011234", "after": "110101199001015678"}
        },
        {
            "id": 5, "name": "银行卡号仿真", "language": "zh",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_bank_card", 
            "config": {},
            "description": "生成随机的银行卡号",
            "example": {"before": "6222021234567890123", "after": "6222029876543210987"}
        },
        {
            "id": 6, "name": "地址仿真", "language": "zh",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_chinese_address", 
            "config": {},
            "description": "生成随机的中国地址",
            "example": {"before": "北京市海淀区中关村大街1号", "after": "上海市浦东新区陆家嘴环路100号"}
        },
        {
            "id": 7, "name": "国家仿真", "language": "all",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_country", 
            "config": {},
            "description": "生成随机的国家名称",
            "example": {"before": "中国", "after": "美国"}
        },
        {
            "id": 8, "name": "英文姓名仿真", "language": "en",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_english_name", 
            "config": {},
            "description": "生成随机的英文姓名",
            "example": {"before": "John Smith", "after": "Mary Johnson"}
        },
        {
            "id": 9, "name": "日文姓名仿真", "language": "ja",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_japanese_name", 
            "config": {},
            "description": "生成随机的日文姓名",
            "example": {"before": "田中太郎", "after": "佐藤花子"}
        },
        {
            "id": 10, "name": "韩文姓名仿真", "language": "ko",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_korean_name", 
            "config": {},
            "description": "生成随机的韩文姓名",
            "example": {"before": "김철수", "after": "이영희"}
        },
        {
            "id": 11, "name": "法文姓名仿真", "language": "fr",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_french_name", 
            "config": {},
            "description": "生成随机的法文姓名",
            "example": {"before": "Martin Bernard", "after": "Thomas Petit"}
        },
        {
            "id": 12, "name": "德文姓名仿真", "language": "de",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_german_name", 
            "config": {},
            "description": "生成随机的德文姓名",
            "example": {"before": "Müller Schmidt", "after": "Schneider Fischer"}
        },
        
        # ========== 关联造数（确定性脱敏）- 中文 ==========
        {
            "id": 31, "name": "姓名关联造数", "language": "zh",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_chinese_name", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性姓名生成，相同原数据+相同密钥=相同结果，支持跨表关联",
            "example": {"before": "张三", "after": "李伟（确定性）"}
        },
        {
            "id": 32, "name": "手机号关联造数", "language": "zh",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_chinese_phone", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性手机号生成，相同原数据+相同密钥=相同结果",
            "example": {"before": "13800138000", "after": "13912345678（确定性）"}
        },
        {
            "id": 33, "name": "身份证号关联造数", "language": "zh",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_chinese_id", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性身份证号生成，支持跨表关联",
            "example": {"before": "110101199001011234", "after": "110101199001015678（确定性）"}
        },
        {
            "id": 34, "name": "银行卡号关联造数", "language": "zh",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_bank_card", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性银行卡号生成，支持跨表关联",
            "example": {"before": "6222021234567890123", "after": "6222029876543210987（确定性）"}
        },
        {
            "id": 35, "name": "地址关联造数", "language": "zh",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_chinese_address", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性地址生成，支持跨表关联",
            "example": {"before": "北京市海淀区中关村大街1号", "after": "上海市浦东新区陆家嘴环路100号（确定性）"}
        },
        {
            "id": 36, "name": "国家关联造数", "language": "all",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_country", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性国家生成，支持跨表关联",
            "example": {"before": "中国", "after": "美国（确定性）"}
        },
        
        # ========== 关联造数（确定性脱敏）- 英文 ==========
        {
            "id": 37, "name": "姓名关联造数-英语", "language": "en",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_english_name", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性英文姓名生成，支持跨表关联",
            "example": {"before": "John Smith", "after": "Mary Johnson（确定性）"}
        },
        {
            "id": 38, "name": "手机号关联造数-英语", "language": "en",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_us_phone", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性美国手机号生成",
            "example": {"before": "(212) 555-1234", "after": "(310) 555-5678（确定性）"}
        },
        {
            "id": 39, "name": "邮箱关联造数-英语", "language": "en",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_email", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性邮箱生成，支持跨表关联",
            "example": {"before": "john@example.com", "after": "mary@test.com（确定性）"}
        },
        {
            "id": 40, "name": "地址关联造数-英语", "language": "en",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_us_address", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性美国地址生成",
            "example": {"before": "123 Main St, New York", "after": "456 Oak Ave, Los Angeles（确定性）"}
        },
        
        # ========== 关联造数（确定性脱敏）- 日文 ==========
        {
            "id": 41, "name": "姓名关联造数-日语", "language": "ja",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_japanese_name", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性日文姓名生成，支持跨表关联",
            "example": {"before": "田中太郎", "after": "佐藤花子（确定性）"}
        },
        {
            "id": 42, "name": "手机号关联造数-日语", "language": "ja",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_jp_phone", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性日本手机号生成",
            "example": {"before": "090-1234-5678", "after": "080-9876-5432（确定性）"}
        },
        {
            "id": 43, "name": "地址关联造数-日语", "language": "ja",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_jp_address", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性日本地址生成",
            "example": {"before": "東京都渋谷区", "after": "大阪府大阪市（确定性）"}
        },
        
        # ========== 关联造数（确定性脱敏）- 韩文 ==========
        {
            "id": 44, "name": "姓名关联造数-韩语", "language": "ko",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_korean_name", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性韩文姓名生成，支持跨表关联",
            "example": {"before": "김철수", "after": "이영희（确定性）"}
        },
        {
            "id": 45, "name": "手机号关联造数-韩语", "language": "ko",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_kr_phone", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性韩国手机号生成",
            "example": {"before": "010-1234-5678", "after": "010-9876-5432（确定性）"}
        },
        {
            "id": 46, "name": "地址关联造数-韩语", "language": "ko",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_kr_address", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性韩国地址生成",
            "example": {"before": "서울특별시 강남구", "after": "부산광역시 해운대구（确定性）"}
        },
        
        # ========== 关联造数（确定性脱敏）- 法文 ==========
        {
            "id": 47, "name": "姓名关联造数-法语", "language": "fr",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_french_name", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性法文姓名生成，支持跨表关联",
            "example": {"before": "Martin Bernard", "after": "Thomas Petit（确定性）"}
        },
        {
            "id": 48, "name": "手机号关联造数-法语", "language": "fr",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_fr_phone", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性法国手机号生成",
            "example": {"before": "06 12 34 56 78", "after": "06 98 76 54 32（确定性）"}
        },
        {
            "id": 49, "name": "地址关联造数-法语", "language": "fr",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_fr_address", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性法国地址生成",
            "example": {"before": "123 Rue de Paris", "after": "456 Avenue de Lyon（确定性）"}
        },
        
        # ========== 关联造数（确定性脱敏）- 德文 ==========
        {
            "id": 50, "name": "姓名关联造数-德语", "language": "de",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_german_name", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性德文姓名生成，支持跨表关联",
            "example": {"before": "Müller Schmidt", "after": "Schneider Fischer（确定性）"}
        },
        {
            "id": 51, "name": "手机号关联造数-德语", "language": "de",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_de_phone", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性德国手机号生成",
            "example": {"before": "+49 170 1234567", "after": "+49 171 9876543（确定性）"}
        },
        {
            "id": 52, "name": "地址关联造数-德语", "language": "de",
            "desensitization_method": "deterministic_simulation",
            "category": "deterministic",
            "method": "deterministic_de_address", 
            "config": {"requires_key": True},
            "description": "基于密钥的确定性德国地址生成",
            "example": {"before": "Berliner Straße 123", "after": "Münchener Weg 456（确定性）"}
        },
        
        # ========== 部分遮盖 ==========
        {
            "id": 13, "name": "姓名部分遮盖", "language": "zh",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "name_mask", 
            "config": {"keep_head": 1, "mask_char": "*"},
            "description": "保留姓氏，名字部分用*代替",
            "example": {"before": "张三", "after": "张*"}
        },
        {
            "id": 14, "name": "手机号部分遮盖", "language": "zh",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "partial_mask", 
            "config": {"keep_head": 3, "keep_tail": 4, "mask_char": "*"},
            "description": "保留前3位和后4位，中间用*代替",
            "example": {"before": "13800138000", "after": "138****8000"}
        },
        {
            "id": 15, "name": "身份证号部分遮盖", "language": "zh",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "partial_mask", 
            "config": {"keep_head": 3, "keep_tail": 4, "mask_char": "*"},
            "description": "保留前3位和后4位，中间用*代替",
            "example": {"before": "110101199001011234", "after": "110***********1234"}
        },
        {
            "id": 16, "name": "银行卡号部分遮盖", "language": "zh",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "partial_mask", 
            "config": {"keep_head": 4, "keep_tail": 4, "mask_char": "*"},
            "description": "保留前4位和后4位，中间用*代替",
            "example": {"before": "6222021234567890123", "after": "6222***********0123"}
        },
        {
            "id": 17, "name": "地址部分遮盖", "language": "zh",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "address_mask", 
            "config": {"keep_head": 6, "mask_char": "*"},
            "description": "保留前6个字符（省市），后面用*代替",
            "example": {"before": "北京市海淀区中关村大街1号", "after": "北京市海***************"}
        },
        {
            "id": 18, "name": "国家部分遮盖", "language": "all",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "partial_mask", 
            "config": {"keep_head": 1, "keep_tail": 1, "mask_char": "*"},
            "description": "保留首尾字符，中间用*代替",
            "example": {"before": "中国", "after": "中*"}
        },
        {
            "id": 19, "name": "邮箱部分遮盖", "language": "en",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "email_mask", 
            "config": {"mask_char": "*"},
            "description": "保留邮箱前2位和域名，中间用*代替",
            "example": {"before": "zhangsan@example.com", "after": "zh******@example.com"}
        },
        {
            "id": 20, "name": "通用等长遮盖", "language": "all",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "equal_length_mask", 
            "config": {"mask_char": "*"},
            "description": "用相同长度的*号替换原始数据",
            "example": {"before": "张三", "after": "**"}
        },
        {
            "id": 21, "name": "通用固定遮盖", "language": "all",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "fixed_mask", 
            "config": {"length": 6, "mask_char": "*"},
            "description": "用固定长度的*号替换原始数据",
            "example": {"before": "张三", "after": "******"}
        },
        
        # ========== 韩语脱敏规则 ==========
        {
            "id": 22, "name": "姓名仿真-韩语", "language": "ko",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_korean_name", 
            "config": {},
            "description": "生成随机的韩文姓名，如김철수、이영희等",
            "example": {"before": "김민수", "after": "박지영"}
        },
        {
            "id": 23, "name": "姓名部分遮盖-韩语", "language": "ko",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "name_mask", 
            "config": {"keep_head": 1, "mask_char": "*"},
            "description": "保留韩文姓氏，名字部分用*代替",
            "example": {"before": "김철수", "after": "김**"}
        },
        
        # ========== 日语脱敏规则 ==========
        {
            "id": 24, "name": "姓名仿真-日语", "language": "ja",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_japanese_name", 
            "config": {},
            "description": "生成随机的日文姓名，如田中太郎、佐藤花子等",
            "example": {"before": "山本一郎", "after": "鈴木美咲"}
        },
        {
            "id": 25, "name": "姓名部分遮盖-日语", "language": "ja",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "name_mask", 
            "config": {"keep_head": 2, "mask_char": "*"},
            "description": "保留日文姓氏，名字部分用*代替",
            "example": {"before": "田中太郎", "after": "田中**"}
        },
        
        # ========== 法语脱敏规则 ==========
        {
            "id": 26, "name": "姓名仿真-法语", "language": "fr",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_french_name", 
            "config": {},
            "description": "生成随机的法文姓名，如Martin Bernard、Thomas Petit等",
            "example": {"before": "Jean Dupont", "after": "Pierre Martin"}
        },
        {
            "id": 27, "name": "姓名部分遮盖-法语", "language": "fr",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "name_mask", 
            "config": {"keep_head": 1, "mask_char": "*"},
            "description": "保留法文名字首字母，其余用*代替",
            "example": {"before": "Jean Dupont", "after": "J*** D*****"}
        },
        
        # ========== 英语脱敏规则 ==========
        {
            "id": 28, "name": "姓名仿真-英语", "language": "en",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_english_name", 
            "config": {},
            "description": "生成随机的英文姓名，如John Smith、Mary Johnson等",
            "example": {"before": "David Brown", "after": "James Wilson"}
        },
        {
            "id": 29, "name": "姓名部分遮盖-英语", "language": "en",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "name_mask", 
            "config": {"keep_head": 1, "mask_char": "*"},
            "description": "保留英文名字首字母，其余用*代替",
            "example": {"before": "John Smith", "after": "J*** S****"}
        },
        {
            "id": 30, "name": "邮箱部分遮盖-英语", "language": "en",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "email_mask", 
            "config": {"mask_char": "*"},
            "description": "保留邮箱前缀前2位和域名，中间用*代替",
            "example": {"before": "john@example.com", "after": "jo**@example.com"}
        },
        
        # ========== 德语脱敏规则 ==========
        {
            "id": 31, "name": "姓名仿真-德语", "language": "de",
            "desensitization_method": "simulation",
            "category": "simulation",
            "method": "random_german_name", 
            "config": {},
            "description": "生成随机的德文姓名，如Müller Schmidt、Schneider Fischer等",
            "example": {"before": "Hans Weber", "after": "Klaus Meyer"}
        },
        {
            "id": 32, "name": "姓名部分遮盖-德语", "language": "de",
            "desensitization_method": "partial_mask",
            "category": "mask",
            "method": "name_mask", 
            "config": {"keep_head": 1, "mask_char": "*"},
            "description": "保留德文名字首字母，其余用*代替",
            "example": {"before": "Hans Weber", "after": "H*** W****"}
        }
    ]
    
    CHINESE_SURNAMES = ["赵", "钱", "孙", "李", "周", "吴", "郑", "王", "冯", "陈", 
                        "褚", "卫", "蒋", "沈", "韩", "杨", "朱", "秦", "尤", "许"]
    CHINESE_NAMES = ["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋",
                     "勇", "艳", "杰", "娟", "涛", "明", "超", "秀英", "霞", "平"]
    
    # 中国地址数据
    CHINESE_PROVINCES = ["北京市", "上海市", "广东省", "浙江省", "江苏省", "四川省", "湖北省", "湖南省"]
    CHINESE_CITIES = {
        "北京市": ["海淀区", "朝阳区", "东城区", "西城区"],
        "上海市": ["浦东新区", "黄浦区", "静安区", "徐汇区"],
        "广东省": ["广州市", "深圳市", "珠海市", "东莞市"],
        "浙江省": ["杭州市", "宁波市", "温州市", "嘉兴市"]
    }
    CHINESE_STREETS = ["中山路", "人民路", "解放路", "建设路", "和平路", "胜利街", "光明路", "文化街"]
    
    # 国家列表
    COUNTRIES = ["中国", "美国", "日本", "韩国", "英国", "法国", "德国", "加拿大", "澳大利亚", "俄罗斯",
                 "印度", "巴西", "意大利", "西班牙", "墨西哥", "印度尼西亚", "土耳其", "沙特阿拉伯"]
    
    ENGLISH_FIRST = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
                     "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica"]
    ENGLISH_LAST = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]
    
    JAPANESE_SURNAMES = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "山本", "中村", "小林", "加藤", "吉田"]
    JAPANESE_NAMES = ["太郎", "次郎", "花子", "一郎", "美咲", "健太", "裕子", "直樹", "愛", "誠"]
    
    KOREAN_SURNAMES = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"]
    KOREAN_NAMES = ["철수", "영희", "민수", "지영", "현우", "수민", "준호", "예진", "도윤", "서연"]
    
    FRENCH_FIRST = ["Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois",
                    "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy", "Roux"]
    FRENCH_LAST = ["Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois",
                   "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy", "Roux"]
    
    GERMAN_FIRST = ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker",
                    "Schulz", "Hoffmann", "Koch", "Bauer", "Richter", "Klein", "Wolf"]
    GERMAN_LAST = ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker",
                   "Schulz", "Hoffmann", "Koch", "Bauer", "Richter", "Klein", "Wolf"]
    
    def __init__(self, custom_rules: Optional[List[Dict]] = None):
        self.rules = self.BUILTIN_RULES + (custom_rules or [])
        self._keys = {}
    
    def set_key(self, key_id: int, key_value: str):
        self._keys[key_id] = key_value
    
    def _get_deterministic_value(self, original: str, key_id: int, generator_func) -> str:
        if key_id not in self._keys:
            return generator_func()
        
        key = self._keys[key_id]
        hash_input = f"{key}:{original}"
        hash_val = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
        
        random.seed(hash_val)
        result = generator_func()
        random.seed()
        
        return result
    
    def desensitize(self, value: str, rule_id: int, key_id: Optional[int] = None) -> str:
        rule = next((r for r in self.rules if r["id"] == rule_id), None)
        if not rule:
            print(f"[WARNING] 规则ID {rule_id} 不存在，返回原始值: {value}")
            return value
        
        method = rule["method"]
        config = rule.get("config", {})
        
        print(f"[DEBUG] 脱敏处理: rule_id={rule_id}, rule_name={rule['name']}, method={method}, value={value[:20] if len(value) > 20 else value}")
        
        # 完全遮盖
        if method == "full_mask":
            return "*"  # 只返回一个*
        
        # 部分遮盖
        elif method == "partial_mask":
            return self._partial_mask(value, config.get("keep_head", 2), 
                                      config.get("keep_tail", 2), config.get("mask_char", "*"))
        elif method == "name_mask":
            return self._name_mask(value, config.get("keep_head", 1), config.get("mask_char", "*"))
        elif method == "address_mask":
            return self._address_mask(value, config.get("keep_head", 6), config.get("mask_char", "*"))
        elif method == "email_mask":
            return self._email_mask(value, config.get("mask_char", "*"))
        elif method == "equal_length_mask":
            return self._equal_length_mask(value, config.get("mask_char", "*"))
        elif method == "fixed_mask":
            return config.get("mask_char", "*") * config.get("length", 6)
        
        # 仿真造数
        elif method == "random_chinese_name":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_name)
            return self._random_chinese_name()
        elif method == "random_chinese_phone":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_phone)
            return self._random_chinese_phone()
        elif method == "random_chinese_id":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_id)
            return self._random_chinese_id()
        elif method == "random_bank_card":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_bank_card)
            return self._random_bank_card()
        elif method == "random_chinese_address":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_address)
            return self._random_chinese_address()
        elif method == "random_country":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_country)
            return self._random_country()
        elif method == "random_english_name":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_english_name)
            return self._random_english_name()
        elif method == "random_japanese_name":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_japanese_name)
            return self._random_japanese_name()
        elif method == "random_korean_name":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_korean_name)
            return self._random_korean_name()
        elif method == "random_french_name":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_french_name)
            return self._random_french_name()
        elif method == "random_german_name":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_german_name)
            return self._random_german_name()
        
        # 关联造数（确定性脱敏）- 中文
        elif method == "deterministic_chinese_name":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_name)
            # 如果没有密钥，降级为普通仿真，但仍要保证与原数据不同
            result = self._random_chinese_name()
            while result == value:
                result = self._random_chinese_name()
            return result
        elif method == "deterministic_chinese_phone":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_phone)
            result = self._random_chinese_phone()
            while result == value:
                result = self._random_chinese_phone()
            return result
        elif method == "deterministic_chinese_id":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_id)
            result = self._random_chinese_id()
            while result == value:
                result = self._random_chinese_id()
            return result
        elif method == "deterministic_bank_card":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_bank_card)
            result = self._random_bank_card()
            while result == value:
                result = self._random_bank_card()
            return result
        elif method == "deterministic_chinese_address":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_address)
            result = self._random_chinese_address()
            while result == value:
                result = self._random_chinese_address()
            return result
        elif method == "deterministic_country":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_country)
            result = self._random_country()
            while result == value:
                result = self._random_country()
            return result
        
        # 关联造数 - 英文
        elif method == "deterministic_english_name":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_english_name)
            result = self._random_english_name()
            while result == value:
                result = self._random_english_name()
            return result
        elif method == "deterministic_us_phone":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_phone)  # 暂时使用中国手机号
            result = self._random_chinese_phone()
            while result == value:
                result = self._random_chinese_phone()
            return result
        elif method == "deterministic_email":
            if key_id:
                return self._get_deterministic_value(value, key_id, lambda: "test@example.com")  # TODO: 实现邮箱生成
            return "test@example.com"
        elif method == "deterministic_us_address":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_address)  # 暂时使用中国地址
            result = self._random_chinese_address()
            while result == value:
                result = self._random_chinese_address()
            return result
        
        # 关联造数 - 日文
        elif method == "deterministic_japanese_name":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_japanese_name)
            result = self._random_japanese_name()
            while result == value:
                result = self._random_japanese_name()
            return result
        elif method == "deterministic_jp_phone":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_phone)
            result = self._random_chinese_phone()
            while result == value:
                result = self._random_chinese_phone()
            return result
        elif method == "deterministic_jp_address":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_address)
            result = self._random_chinese_address()
            while result == value:
                result = self._random_chinese_address()
            return result
        
        # 关联造数 - 韩文
        elif method == "deterministic_korean_name":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_korean_name)
            result = self._random_korean_name()
            while result == value:
                result = self._random_korean_name()
            return result
        elif method == "deterministic_kr_phone":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_phone)
            result = self._random_chinese_phone()
            while result == value:
                result = self._random_chinese_phone()
            return result
        elif method == "deterministic_kr_address":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_address)
            result = self._random_chinese_address()
            while result == value:
                result = self._random_chinese_address()
            return result
        
        # 关联造数 - 法文
        elif method == "deterministic_french_name":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_french_name)
            result = self._random_french_name()
            while result == value:
                result = self._random_french_name()
            return result
        elif method == "deterministic_fr_phone":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_phone)
            result = self._random_chinese_phone()
            while result == value:
                result = self._random_chinese_phone()
            return result
        elif method == "deterministic_fr_address":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_address)
            result = self._random_chinese_address()
            while result == value:
                result = self._random_chinese_address()
            return result
        
        # 关联造数 - 德文
        elif method == "deterministic_german_name":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_german_name)
            result = self._random_german_name()
            while result == value:
                result = self._random_german_name()
            return result
        elif method == "deterministic_de_phone":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_phone)
            result = self._random_chinese_phone()
            while result == value:
                result = self._random_chinese_phone()
            return result
        elif method == "deterministic_de_address":
            if key_id:
                return self._get_deterministic_value(value, key_id, self._random_chinese_address)
            result = self._random_chinese_address()
            while result == value:
                result = self._random_chinese_address()
            return result
        
        return value
    
    def _partial_mask(self, value: str, keep_head: int, keep_tail: int, mask_char: str) -> str:
        if len(value) <= keep_head + keep_tail:
            return mask_char * len(value)
        return value[:keep_head] + mask_char * (len(value) - keep_head - keep_tail) + value[-keep_tail:]
    
    def _name_mask(self, value: str, keep_head: int, mask_char: str) -> str:
        if len(value) <= keep_head:
            return mask_char * len(value)
        return value[:keep_head] + mask_char * (len(value) - keep_head)
    
    def _address_mask(self, value: str, keep_head: int, mask_char: str) -> str:
        if len(value) <= keep_head:
            return mask_char * len(value)
        return value[:keep_head] + mask_char * (len(value) - keep_head)
    
    def _email_mask(self, value: str, mask_char: str) -> str:
        parts = value.split("@")
        if len(parts) != 2:
            return self._partial_mask(value, 2, 2, mask_char)
        local = parts[0]
        domain = parts[1]
        masked_local = local[:2] + mask_char * max(1, len(local) - 2)
        return f"{masked_local}@{domain}"
    
    def _equal_length_mask(self, value: str, mask_char: str) -> str:
        return mask_char * len(value)
    
    def _random_chinese_name(self) -> str:
        surname = random.choice(self.CHINESE_SURNAMES)
        name_count = random.randint(1, 2)
        name = "".join(random.choice(self.CHINESE_NAMES) for _ in range(name_count))
        return surname + name
    
    def _random_english_name(self) -> str:
        first = random.choice(self.ENGLISH_FIRST)
        last = random.choice(self.ENGLISH_LAST)
        return f"{first} {last}"
    
    def _random_japanese_name(self) -> str:
        surname = random.choice(self.JAPANESE_SURNAMES)
        name = random.choice(self.JAPANESE_NAMES)
        return f"{surname} {name}"
    
    def _random_korean_name(self) -> str:
        surname = random.choice(self.KOREAN_SURNAMES)
        name_count = random.randint(2, 3)
        name = "".join(random.choice(self.KOREAN_NAMES) for _ in range(name_count))
        return f"{surname}{name}"
    
    def _random_french_name(self) -> str:
        first = random.choice(self.FRENCH_FIRST)
        last = random.choice(self.FRENCH_LAST)
        return f"{first} {last}"
    
    def _random_german_name(self) -> str:
        first = random.choice(self.GERMAN_FIRST)
        last = random.choice(self.GERMAN_LAST)
        return f"{first} {last}"
    
    def _random_chinese_phone(self) -> str:
        """生成随机中国手机号"""
        prefix = random.choice(["138", "139", "137", "136", "135", "134", "159", "158", "157", "150",
                                "151", "152", "188", "187", "183", "182", "178", "198", "199"])
        suffix = "".join([str(random.randint(0, 9)) for _ in range(8)])
        return prefix + suffix
    
    def _random_chinese_id(self) -> str:
        """生成随机中国身份证号"""
        # 地区码（前6位）
        area_codes = ["110101", "110102", "310101", "310104", "440101", "440301", "330101", "320101"]
        area = random.choice(area_codes)
        
        # 出生日期（8位）
        year = random.randint(1970, 2005)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        birthday = f"{year:04d}{month:02d}{day:02d}"
        
        # 顺序码（3位）
        sequence = "".join([str(random.randint(0, 9)) for _ in range(3)])
        
        # 校验码（1位）
        check_code = str(random.randint(0, 9)) if random.random() > 0.1 else "X"
        
        return area + birthday + sequence + check_code
    
    def _random_bank_card(self) -> str:
        """生成随机银行卡号"""
        # 银行BIN码（前6位）
        bin_codes = ["622202", "622203", "622208", "621700", "621799", "622848", "622849"]
        bin_code = random.choice(bin_codes)
        
        # 中间数字（9位）
        middle = "".join([str(random.randint(0, 9)) for _ in range(9)])
        
        # 校验位（1位）
        check = str(random.randint(0, 9))
        
        return bin_code + middle + check
    
    def _random_chinese_address(self) -> str:
        """生成随机中国地址"""
        province = random.choice(self.CHINESE_PROVINCES)
        
        if province in self.CHINESE_CITIES:
            city = random.choice(self.CHINESE_CITIES[province])
        else:
            city = f"{province[:-1]}市"
        
        street = random.choice(self.CHINESE_STREETS)
        number = random.randint(1, 999)
        
        return f"{province}{city}{street}{number}号"
    
    def _random_country(self) -> str:
        """生成随机国家名称"""
        return random.choice(self.COUNTRIES)
    
    def preview_desensitization(self, df, field_rules: Dict[str, int], key_id: Optional[int] = None, 
                                 limit: int = 10) -> List[Dict]:
        previews = []
        sample_df = df.head(limit)
        
        for idx, row in sample_df.iterrows():
            preview = {"row_index": idx, "columns": {}}
            for col, rule_id in field_rules.items():
                if col in row:
                    original = str(row[col])
                    desensitized = self.desensitize(original, rule_id, key_id)
                    preview["columns"][col] = {
                        "original": original,
                        "desensitized": desensitized
                    }
            previews.append(preview)
        
        return previews
    
    def preview_auto_desensitization(self, df, key_id: Optional[int] = None, 
                                      limit: int = 10) -> List[Dict]:
        """
        自动识别并脱敏预览
        为每个字段智能匹配最合适的脱敏规则
        """
        from app.services.detection_engine import DetectionEngine
        import pandas as pd
        
        detection_engine = DetectionEngine()
        previews = []
        sample_df = df.head(limit)
        
        # 对每一行数据进行自动识别和脱敏
        for idx, row in sample_df.iterrows():
            preview = {"row_index": idx, "columns": {}}
            
            for col in df.columns:
                if col in row:
                    original = str(row[col])
                    if not original or original == "nan":
                        continue
                    
                    # 使用检测引擎识别该字段的类型
                    matches = detection_engine.scan_text(original, column_name=col)
                    
                    if matches:
                        # 选择置信度最高的匹配
                        best_match = max(matches, key=lambda m: m.confidence)
                        
                        # 根据检测结果找到对应的脱敏规则
                        rule_id = self._find_rule_by_detection(best_match)
                        
                        if rule_id:
                            desensitized = self.desensitize(original, rule_id, key_id)
                            
                            # 获取规则信息
                            rule_info = self._get_rule_info(rule_id)
                            
                            preview["columns"][col] = {
                                "original": original,
                                "desensitized": desensitized,
                                "rule_info": {
                                    "rule_id": rule_id,
                                    "rule_name": rule_info.get("name", ""),
                                    "language": rule_info.get("language", "all"),
                                    "confidence": round(best_match.confidence, 2)
                                }
                            }
                    else:
                        # 未检测到敏感信息，使用默认规则（完全遮盖）
                        default_rule_id = 1  # 完全遮盖规则ID
                        desensitized = self.desensitize(original, default_rule_id, key_id)
                        preview["columns"][col] = {
                            "original": original,
                            "desensitized": desensitized,
                            "rule_info": {
                                "rule_id": default_rule_id,
                                "rule_name": "完全遮盖",
                                "language": "all",
                                "confidence": 0.5
                            }
                        }
            
            previews.append(preview)
        
        return previews
    
    def _find_rule_by_detection(self, match) -> Optional[int]:
        """根据检测结果找到对应的脱敏规则ID"""
        # 检测规则ID → 脱敏规则ID 映射
        mapping = {
            # ========== 手机号 ==========
            1: 3,    # 中国大陆手机号 → 手机号仿真
            15: 3,   # 美国手机号 → 手机号仿真
            19: 3,   # 日本手机号 → 手机号仿真
            22: 3,   # 韩国手机号 → 手机号仿真
            25: 3,   # 法国手机号 → 手机号仿真
            28: 3,   # 德国手机号 → 手机号仿真
            
            # ========== 身份证 ==========
            2: 4,    # 中国大陆身份证 → 身份证号仿真
            23: 4,   # 韩国身份证号 → 身份证号仿真
            
            # ========== 姓名 ==========
            3: 2,    # 中文姓名 → 姓名仿真
            6: 8,    # 英文姓名 → 英文姓名仿真
            9: 9,    # 日文姓名 → 日文姓名仿真
            10: 10,  # 韩文姓名 → 韩文姓名仿真
            11: 11,  # 法文姓名 → 法文姓名仿真
            12: 12,  # 德文姓名 → 德文姓名仿真
            
            # ========== 银行卡/信用卡 ==========
            4: 5,    # 中国银行卡号 → 银行卡号仿真
            14: 5,   # 信用卡号 → 银行卡号仿真
            
            # ========== 邮箱 ==========
            7: 19,   # 邮箱地址 → 邮箱部分遮盖
            
            # ========== 地址 ==========
            5: 6,    # 中文地址关键词 → 地址仿真
            18: 6,   # 英文地址关键词 → 地址仿真
            21: 6,   # 日文地址关键词 → 地址仿真
            24: 6,   # 韩文地址关键词 → 地址仿真
            27: 6,   # 法文地址关键词 → 地址仿真
            30: 6,   # 德文地址关键词 → 地址仿真
            
            # ========== 国家 ==========
            31: 7,   # 国家名称 → 国家仿真
        }
        
        return mapping.get(match.rule_id)
    
    def _get_rule_info(self, rule_id: int) -> Dict:
        """获取规则信息"""
        for rule in self.rules:
            if rule["id"] == rule_id:
                return {
                    "name": rule["name"],
                    "language": rule["language"],
                    "desensitization_method": rule.get("desensitization_method", "")
                }
        return {"name": "未知规则", "language": "all"}
    
    def process_dataframe(self, df, field_rules: Dict[str, int], key_id: Optional[int] = None,
                          progress_callback=None) -> Tuple[Any, List[DesensitizationMatch]]:
        import pandas as pd
        
        result_df = df.copy()
        matches = []
        total_rows = len(df)
        
        for idx, row in df.iterrows():
            for col, rule_id in field_rules.items():
                if col in row:
                    original = str(row[col])
                    if original and original != "nan":
                        desensitized = self.desensitize(original, rule_id, key_id)
                        result_df.at[idx, col] = desensitized
                        matches.append(DesensitizationMatch(
                            row_index=idx,
                            column_name=col,
                            original_value=original,
                            desensitized_value=desensitized,
                            rule_id=rule_id,
                            rule_name=next((r["name"] for r in self.rules if r["id"] == rule_id), "")
                        ))
            
            if progress_callback and idx % 100 == 0:
                progress_callback(idx + 1, total_rows)
        
        if progress_callback:
            progress_callback(total_rows, total_rows)
        
        return result_df, matches
    
    def process_auto_desensitization(self, df, key_id: Optional[int] = None,
                                      progress_callback=None) -> Tuple[Any, List[DesensitizationMatch]]:
        """
        自动识别并处理全量数据脱敏
        为每个字段智能匹配最合适的脱敏规则
        """
        from app.services.detection_engine import DetectionEngine
        import pandas as pd
        
        detection_engine = DetectionEngine()
        result_df = df.copy()
        matches = []
        total_rows = len(df)
        
        for idx, row in df.iterrows():
            for col in df.columns:
                if col in row:
                    original = str(row[col])
                    if not original or original == "nan":
                        continue
                    
                    # 使用检测引擎识别该字段的类型
                    matches_list = detection_engine.scan_text(original, column_name=col)
                    
                    if matches_list:
                        # 选择置信度最高的匹配
                        best_match = max(matches_list, key=lambda m: m.confidence)
                        
                        # 根据检测结果找到对应的脱敏规则
                        rule_id = self._find_rule_by_detection(best_match)
                        
                        if rule_id:
                            desensitized = self.desensitize(original, rule_id, key_id)
                            result_df.at[idx, col] = desensitized
                            
                            rule_name = next((r["name"] for r in self.rules if r["id"] == rule_id), "")
                            matches.append(DesensitizationMatch(
                                row_index=idx,
                                column_name=col,
                                original_value=original,
                                desensitized_value=desensitized,
                                rule_id=rule_id,
                                rule_name=rule_name
                            ))
                    else:
                        # 未检测到敏感信息，使用默认规则（完全遮盖）
                        default_rule_id = 1
                        desensitized = self.desensitize(original, default_rule_id, key_id)
                        result_df.at[idx, col] = desensitized
                        
                        matches.append(DesensitizationMatch(
                            row_index=idx,
                            column_name=col,
                            original_value=original,
                            desensitized_value=desensitized,
                            rule_id=default_rule_id,
                            rule_name="完全遮盖"
                        ))
            
            if progress_callback and idx % 100 == 0:
                progress_callback(idx + 1, total_rows)
        
        if progress_callback:
            progress_callback(total_rows, total_rows)
        
        return result_df, matches
