import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.services.language_detector import LanguageDetector
from app.services.address_parser import AddressParser, AddressInfo, AddressIdentifier


@dataclass
class DetectionMatch:
    row_index: int
    column_name: str
    detected_language: str
    rule_id: int
    rule_name: str
    rule_type: str
    matched_content: str
    confidence: float
    desensitization_suggestion: str


class AddressType(Enum):
    """地址类型枚举"""
    FULL_ADDRESS = "完整地址"           # 省市区街道详细地址
    PROVINCE_CITY = "省市地址"          # 只有省市
    CITY_DISTRICT = "市区地址"          # 只有市区
    DETAIL_ADDRESS = "详细地址"         # 街道门牌号等
    POBOX = "邮政信箱"                 # 邮政信箱
    RURAL_ADDRESS = "农村地址"         # 包含村组的地址
    COMPANY_ADDRESS = "企业地址"       # 包含企业名称的地址
    UNKNOWN = "未知"


class AddressLevel(Enum):
    """地址级别"""
    COUNTRY = "国家"
    PROVINCE = "省级"        # 省/自治区/直辖市/特别行政区
    CITY = "地市级"          # 地级市/自治州/地区
    DISTRICT = "区县级"      # 市辖区/县级市/县/自治县
    STREET = "街道级"        # 街道/镇/乡
    COMMUNITY = "社区级"     # 社区/村/居委会
    BUILDING = "建筑级"      # 小区/大厦/楼栋
    ROOM = "房间级"          # 楼层/门牌号


@dataclass
class AddressInfo:
    """地址信息"""
    full_address: str                          # 完整地址
    country: str = ""                          # 国家
    province: str = ""                         # 省/直辖市
    city: str = ""                             # 地级市
    district: str = ""                         # 区/县/县级市
    street: str = ""                           # 街道/镇/乡
    community: str = ""                        # 社区/村
    building: str = ""                         # 小区/大厦/楼栋
    room: str = ""                             # 门牌号/室
    detail: str = ""                           # 其他详细描述
    postal_code: str = ""                      # 邮政编码
    phone: str = ""                            # 联系电话（从地址中提取）
    contact_person: str = ""                   # 联系人（从地址中提取）
    
    # 识别信息
    confidence: float = 0.0                    # 置信度
    address_type: AddressType = AddressType.UNKNOWN
    parsed_level: AddressLevel = AddressLevel.PROVINCE
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'full_address': self.full_address,
            'country': self.country,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'street': self.street,
            'community': self.community,
            'building': self.building,
            'room': self.room,
            'detail': self.detail,
            'postal_code': self.postal_code,
            'confidence': self.confidence,
            'address_type': self.address_type.value,
            'parsed_level': self.parsed_level.value
        }


class DetectionEngine:
    BUILTIN_RULES = [
        # ==================== 中文规则 (zh) ====================
        {
            "id": 1, "name": "中国大陆手机号", "language": "zh", "rule_type": "regex",
            "pattern": r"1[3-9]\d{9}",
            "example": "13800138000",
            "suggestion": "手机号脱敏"
        },
        {
            "id": 2, "name": "中国大陆身份证", "language": "zh", "rule_type": "regex",
            "pattern": r"[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]",
            "example": "110101199001011234",
            "suggestion": "身份证脱敏"
        },
        {
            "id": 3, "name": "中文姓名", "language": "zh", "rule_type": "regex",
            "pattern": r"[\u4e00-\u9fff]{2,4}",
            "example": "张三",
            "suggestion": "姓名脱敏"
        },
        {
            "id": 4, "name": "中国银行卡号", "language": "zh", "rule_type": "regex",
            "pattern": r"\d{16,19}",
            "example": "6222021234567890123",
            "suggestion": "银行卡号脱敏"
        },
        {
            "id": 5, "name": "中文地址关键词", "language": "zh", "rule_type": "keyword",
            "keywords": ["省", "市", "区", "县", "街道", "路", "号", "小区", "栋", "单元", "室"],
            "example": "北京市海淀区",
            "suggestion": "地址脱敏"
        },
        {
            "id": 13, "name": "密码关键词", "language": "zh", "rule_type": "keyword",
            "keywords": ["密码", "口令", "pass", "password", "pwd", "密钥", "secret"],
            "example": "password=123456",
            "suggestion": "密码脱敏"
        },
        
        # ==================== 英文规则 (en) ====================
        {
            "id": 6, "name": "英文姓名", "language": "en", "rule_type": "regex",
            "pattern": r"[A-Z][a-z]+\s+[A-Z][a-z]+",
            "example": "John Smith",
            "suggestion": "姓名脱敏"
        },
        {
            "id": 7, "name": "邮箱地址", "language": "en", "rule_type": "regex",
            "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "example": "user@example.com",
            "suggestion": "邮箱脱敏"
        },
        {
            "id": 8, "name": "美国SSN", "language": "en", "rule_type": "regex",
            "pattern": r"\d{3}-\d{2}-\d{4}",
            "example": "123-45-6789",
            "suggestion": "SSN脱敏"
        },
        {
            "id": 14, "name": "信用卡号", "language": "en", "rule_type": "regex",
            "pattern": r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",
            "example": "1234-5678-9012-3456",
            "suggestion": "信用卡脱敏"
        },
        {
            "id": 15, "name": "美国手机号", "language": "en", "rule_type": "regex",
            "pattern": r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            "example": "+1-234-567-8900",
            "suggestion": "手机号脱敏"
        },
        {
            "id": 16, "name": "IP地址", "language": "en", "rule_type": "regex",
            "pattern": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "example": "192.168.1.1",
            "suggestion": "IP地址脱敏"
        },
        {
            "id": 17, "name": "URL地址", "language": "en", "rule_type": "regex",
            "pattern": r"https?://[^\s]+",
            "example": "https://www.example.com",
            "suggestion": "URL脱敏"
        },
        {
            "id": 18, "name": "英文地址关键词", "language": "en", "rule_type": "keyword",
            "keywords": ["street", "st", "avenue", "ave", "road", "rd", "boulevard", "blvd", "drive", "dr", "lane", "ln", "apt", "suite"],
            "example": "123 Main Street",
            "suggestion": "地址脱敏"
        },
        
        # ==================== 日文规则 (ja) ====================
        {
            "id": 9, "name": "日文姓名", "language": "ja", "rule_type": "regex",
            "pattern": r"[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]{2,5}",
            "example": "田中太郎",
            "suggestion": "姓名脱敏"
        },
        {
            "id": 19, "name": "日本手机号", "language": "ja", "rule_type": "regex",
            "pattern": r"0[789]0-\d{4}-\d{4}",
            "example": "090-1234-5678",
            "suggestion": "手机号脱敏"
        },
        {
            "id": 20, "name": "日本邮编", "language": "ja", "rule_type": "regex",
            "pattern": r"\d{3}-\d{4}",
            "example": "123-4567",
            "suggestion": "邮编脱敏"
        },
        {
            "id": 21, "name": "日文地址关键词", "language": "ja", "rule_type": "keyword",
            "keywords": ["都", "道", "府", "県", "市", "区", "町", "村", "丁目", "番地", "号", "公寓", "マンション"],
            "example": "東京都渋谷区",
            "suggestion": "地址脱敏"
        },
        
        # ==================== 韩文规则 (ko) ====================
        {
            "id": 10, "name": "韩文姓名", "language": "ko", "rule_type": "regex",
            "pattern": r"[\uac00-\ud7af]{2,4}",
            "example": "김철수",
            "suggestion": "姓名脱敏"
        },
        {
            "id": 22, "name": "韩国手机号", "language": "ko", "rule_type": "regex",
            "pattern": r"010-\d{4}-\d{4}",
            "example": "010-1234-5678",
            "suggestion": "手机号脱敏"
        },
        {
            "id": 23, "name": "韩国身份证号", "language": "ko", "rule_type": "regex",
            "pattern": r"\d{6}-\d{7}",
            "example": "900101-1234567",
            "suggestion": "身份证号脱敏"
        },
        {
            "id": 24, "name": "韩文地址关键词", "language": "ko", "rule_type": "keyword",
            "keywords": ["시", "도", "구", "군", "동", "리", "가", "로", "길", "아파트", "번지"],
            "example": "서울특별시 강남구",
            "suggestion": "地址脱敏"
        },
        
        # ==================== 法文规则 (fr) ====================
        {
            "id": 11, "name": "法文姓名", "language": "fr", "rule_type": "regex",
            "pattern": r"[A-ZÀÂÄÉÈÊËÏÎÔÙÛÜÇ][a-zàâäéèêëïîôùûüç]+\s+[A-ZÀÂÄÉÈÊËÏÎÔÙÛÜÇ][a-zàâäéèêëïîôùûüç]+",
            "example": "Martin Blot",
            "suggestion": "姓名脱敏"
        },
        {
            "id": 25, "name": "法国手机号", "language": "fr", "rule_type": "regex",
            "pattern": r"(?:\+?33|0)[67]\d{8}",
            "example": "+33612345678",
            "suggestion": "手机号脱敏"
        },
        {
            "id": 26, "name": "法国邮编", "language": "fr", "rule_type": "regex",
            "pattern": r"\b\d{5}\b",
            "example": "75001",
            "suggestion": "邮编脱敏"
        },
        {
            "id": 27, "name": "法文地址关键词", "language": "fr", "rule_type": "keyword",
            "keywords": ["rue", "avenue", "boulevard", "bd", "place", "impasse", "allée", "résidence", "appartement", "apt"],
            "example": "123 Rue de la Paix",
            "suggestion": "地址脱敏"
        },
        
        # ==================== 德文规则 (de) ====================
        {
            "id": 12, "name": "德文姓名", "language": "de", "rule_type": "regex",
            "pattern": r"[A-ZÄÖÜẞ][a-zäöüß]+\s+[A-ZÄÖÜẞ][a-zäöüß]+",
            "example": "Anto Jungfer",
            "suggestion": "姓名脱敏"
        },
        {
            "id": 28, "name": "德国手机号", "language": "de", "rule_type": "regex",
            "pattern": r"(?:\+?49|0)1[5-7]\d{8,9}",
            "example": "+4915123456789",
            "suggestion": "手机号脱敏"
        },
        {
            "id": 29, "name": "德国邮编", "language": "de", "rule_type": "regex",
            "pattern": r"\b\d{5}\b",
            "example": "10115",
            "suggestion": "邮编脱敏"
        },
        {
            "id": 30, "name": "德文地址关键词", "language": "de", "rule_type": "keyword",
            "keywords": ["straße", "str", "allee", "platz", "weg", "gasse", "ring", "haus", "wohnung", "wg"],
            "example": "Hauptstraße 123",
            "suggestion": "地址脱敏"
        },
        
        # ==================== 国家识别规则 (all) ====================
        {
            "id": 31, "name": "国家名称", "language": "all", "rule_type": "keyword",
            "keywords": [
                # 中文国家名
                "中国", "日本", "韩国", "法国", "德国", "英国", "美国", "俄罗斯", "意大利", "西班牙",
                "加拿大", "澳大利亚", "巴西", "印度", "墨西哥", "荷兰", "瑞士", "瑞典", "挪威", "丹麦",
                "芬兰", "波兰", "比利时", "奥地利", "葡萄牙", "希腊", "土耳其", "泰国", "越南", "新加坡",
                "马来西亚", "印度尼西亚", "菲律宾", "埃及", "南非", "阿根廷", "智利", "哥伦比亚",
                # 英文国家名
                "China", "Japan", "Korea", "France", "Germany", "United Kingdom", "UK", "United States", "USA",
                "Russia", "Italy", "Spain", "Canada", "Australia", "Brazil", "India", "Mexico",
                "Netherlands", "Switzerland", "Sweden", "Norway", "Denmark", "Finland", "Poland",
                "Belgium", "Austria", "Portugal", "Greece", "Turkey", "Thailand", "Vietnam", "Singapore",
                "Malaysia", "Indonesia", "Philippines", "Egypt", "South Africa", "Argentina", "Chile", "Colombia",
                # 日文国家名
                "中国", "日本", "韓国", "フランス", "ドイツ", "イギリス", "アメリカ", "ロシア", "イタリア",
                # 韩文国家名
                "중국", "일본", "한국", "프랑스", "독일", "영국", "미국", "러시아", "이탈리아",
                # 法文国家名
                "Chine", "Japon", "Corée", "France", "Allemagne", "Royaume-Uni", "États-Unis", "Russie", "Italie",
                # 德文国家名
                "China", "Japan", "Korea", "Frankreich", "Deutschland", "Vereinigtes Königreich", "Vereinigte Staaten",
                "Russland", "Italien", "Spanien"
            ],
            "example": "中国",
            "suggestion": "国家脱敏"
        }
    ]
    
    def __init__(self, custom_rules: Optional[List[Dict]] = None):
        self.rules = self.BUILTIN_RULES + (custom_rules or [])
        self._compile_rules()
    
    def _compile_rules(self):
        for rule in self.rules:
            if rule.get("rule_type") == "regex" and "pattern" in rule:
                try:
                    rule["_compiled"] = re.compile(rule["pattern"])
                except re.error:
                    rule["_compiled"] = None
    
    @staticmethod
    def luhn_check(card_number: str) -> bool:
        """
        Luhn算法校验银行卡号
        
        Args:
            card_number: 银行卡号字符串
            
        Returns:
            是否通过Luhn校验
        """
        if not card_number or not card_number.isdigit():
            return False
        
        digits = [int(d) for d in card_number]
        total = 0
        
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                doubled = digit * 2
                if doubled > 9:
                    doubled -= 9
                total += doubled
            else:
                total += digit
        
        return total % 10 == 0
    
    # ==================== 身份证识别相关 ====================
    
    # 身份证地区码（前6位），包含主要省市
    ID_CARD_AREA_CODES = {
        "110000": "北京市", "110101": "北京市东城区", "110102": "北京市西城区",
        "110105": "北京市朝阳区", "110106": "北京市丰台区", "110107": "北京市石景山区",
        "110108": "北京市海淀区", "110109": "北京市门头沟区", "110111": "北京市房山区",
        "110112": "北京市通州区", "110113": "北京市顺义区", "110114": "北京市昌平区",
        "110115": "北京市大兴区", "110116": "北京市怀柔区", "110117": "北京市平谷区",
        "120000": "天津市", "120101": "天津市和平区", "120102": "天津市河东区",
        "120103": "天津市河区", "120104": "天津市南开区", "120105": "天津市河北区",
        "120106": "天津市红桥区", "120110": "天津市东丽区", "120111": "天津市西青区",
        "120112": "天津市津南区", "120113": "天津市北辰区", "120114": "天津市武清区",
        "120115": "天津市宝坻区", "120116": "天津市滨海新区",
        "310000": "上海市", "310101": "上海市黄浦区", "310104": "上海市徐汇区",
        "310105": "上海市长宁区", "310106": "上海市静安区", "310107": "上海市普陀区",
        "310109": "上海市虹口区", "310110": "上海市杨浦区", "310112": "上海市闵行区",
        "310113": "上海市宝山区", "310114": "上海市嘉定区", "310115": "上海市浦东新区",
        "310116": "上海市金山区", "310117": "上海市松江区", "310118": "上海市青浦区",
        "310120": "上海市奉贤区", "310151": "上海市崇明区",
        "500000": "重庆市", "500101": "重庆市万州区", "500102": "重庆市涪陵区",
        "500103": "重庆市渝中区", "500104": "重庆市大渡口区", "500105": "重庆市江北区",
        "500106": "重庆市沙坪坝区", "500107": "重庆市九龙坡区", "500108": "重庆市南岸区",
        "500109": "重庆市北碚区", "500110": "重庆市綦江区", "500111": "重庆市大足区",
        "500112": "重庆市渝北区", "500113": "重庆市巴南区", "500114": "重庆市黔江区",
        "500115": "重庆市长寿区", "500116": "重庆市江津区", "500117": "重庆市合川区",
        "500118": "重庆市永川区", "500119": "重庆市南川区",
        "440000": "广东省", "440100": "广州市", "440103": "广州市荔湾区",
        "440104": "广州市越秀区", "440105": "广州市海珠区", "440106": "广州市天河区",
        "440111": "广州市白云区", "440112": "广州市黄埔区", "440113": "广州市番禺区",
        "440114": "广州市花都区", "440115": "广州市南沙区", "440117": "广州市从化区",
        "440118": "广州市增城区", "440300": "深圳市", "440303": "深圳市罗湖区",
        "440304": "深圳市福田区", "440305": "深圳市南山区", "440306": "深圳市宝安区",
        "440307": "深圳市龙岗区", "440308": "深圳市盐田区", "440309": "深圳市龙华区",
        "440310": "深圳市坪山区", "440311": "深圳市光明区",
        "330000": "浙江省", "330100": "杭州市", "330102": "杭州市上城区",
        "330103": "杭州市下城区", "330104": "杭州市江干区", "330105": "杭州市拱墅区",
        "330106": "杭州市西湖区", "330108": "杭州市滨江区", "330109": "杭州市萧山区",
        "330110": "杭州市余杭区", "330111": "杭州市富阳区", "330112": "杭州市临安区",
        "330200": "宁波市", "330203": "宁波市海曙区", "330205": "宁波市江北区",
        "330206": "宁波市北仑区", "330211": "宁波市镇海区", "330212": "宁波市鄞州区",
        "320000": "江苏省", "320100": "南京市", "320102": "南京市玄武区",
        "320104": "南京市秦淮区", "320105": "南京市建邺区", "320106": "南京市鼓楼区",
        "320111": "南京市浦口区", "320113": "南京市栖霞区", "320114": "南京市雨花台区",
        "320115": "南京市江宁区", "320116": "南京市六合区", "320117": "南京市溧水区",
        "320118": "南京市高淳区", "320500": "苏州市", "320505": "苏州市虎丘区",
        "320506": "苏州市吴中区", "320507": "苏州市相城区", "320508": "苏州市姑苏区",
        "320509": "苏州市吴江区",
        "350000": "福建省", "350100": "福州市", "350200": "厦门市",
        "350500": "泉州市", "350600": "漳州市", "350700": "南平市",
        "360000": "江西省", "360100": "南昌市", "360200": "景德镇市",
        "370000": "山东省", "370100": "济南市", "370200": "青岛市",
        "370300": "淄博市", "370600": "烟台市", "370700": "潍坊市",
        "410000": "河南省", "410100": "郑州市", "410200": "开封市",
        "420000": "湖北省", "420100": "武汉市", "420200": "黄石市",
        "430000": "湖南省", "430100": "长沙市", "430200": "株洲市",
        "450000": "广西壮族自治区", "450100": "南宁市", "450200": "柳州市",
        "460000": "海南省", "460100": "海口市", "460200": "三亚市",
        "510000": "四川省", "510100": "成都市", "510104": "成都市锦江区",
        "510105": "成都市青羊区", "510106": "成都市金牛区", "510107": "成都市武侯区",
        "510108": "成都市成华区", "510112": "成都市龙泉驿区", "510113": "成都市青白江区",
        "510114": "成都市新都区", "510115": "成都市温江区", "510116": "成都市双流区",
        "510117": "成都市郫都区", "510118": "成都市新津区", "510121": "成都市金堂县",
        "510124": "成都市大邑县", "510129": "成都市蒲江县", "510131": "成都市新津县",
        "510132": "成都市都江堰市", "510181": "成都市彭州市", "510182": "成都市邛崃市",
        "510183": "成都市崇州市", "510184": "成都市简阳市",
        "520000": "贵州省", "520100": "贵阳市", "530000": "云南省", "530100": "昆明市",
        "540000": "西藏自治区", "540100": "拉萨市",
        "610000": "陕西省", "610100": "西安市", "610102": "西安市新城区",
        "610103": "西安市碑林区", "610104": "西安市莲湖区", "610111": "西安市灞桥区",
        "610112": "西安市未央区", "610113": "西安市雁塔区", "610114": "西安市阎良区",
        "610115": "西安市临潼区", "610116": "西安市长安区", "610117": "西安市高陵区",
        "610118": "西安市鄠邑区",
        "620000": "甘肃省", "620100": "兰州市", "630000": "青海省", "630100": "西宁市",
        "640000": "宁夏回族自治区", "640100": "银川市",
        "650000": "新疆维吾尔自治区", "650100": "乌鲁木齐市",
        "210000": "辽宁省", "210100": "沈阳市", "210200": "大连市",
        "220000": "吉林省", "220100": "长春市", "220200": "吉林市",
        "230000": "黑龙江省", "230100": "哈尔滨市", "230200": "齐齐哈尔市",
        "130000": "河北省", "130100": "石家庄市", "130200": "唐山市",
        "140000": "山西省", "140100": "太原市", "140200": "大同市",
        "150000": "内蒙古自治区", "150100": "呼和浩特市", "150200": "包头市",
        "210300": "鞍山市", "210400": "抚顺市", "210500": "本溪市", "210600": "丹东市",
        "210700": "锦州市", "210800": "营口市", "210900": "阜新市", "211000": "辽阳市",
        "211100": "盘锦市", "211200": "铁岭市", "211300": "朝阳市", "211400": "葫芦岛市",
    }
    
    # 身份证校验权重
    ID_CARD_WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    ID_CARD_CHECK_CODES = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    @staticmethod
    def validate_id_card(id_number: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        验证18位身份证号
        
        规则：
        1. 长度18位
        2. 前17位为数字，最后一位为数字或X
        3. 前6位为合法地区码
        4. 第7-14位为合法日期（YYYYMMDD）
        5. 第17位为性别标识（奇男偶女）
        6. 第18位为校验位
        
        Args:
            id_number: 身份证号
            
        Returns:
            (是否有效, 描述, 元数据)
        """
        metadata = {}
        
        # 格式检查
        if not re.match(r'^\d{17}[\dXx]$', id_number):
            return False, "格式不符合18位身份证号", metadata
        
        # 地区码检查
        area_code = id_number[:6]
        if area_code in DetectionEngine.ID_CARD_AREA_CODES:
            metadata['area'] = DetectionEngine.ID_CARD_AREA_CODES[area_code]
            metadata['area_code_valid'] = True
        else:
            # 放宽条件，因为地区码库可能不完整
            metadata['area'] = '未知地区'
            metadata['area_code_valid'] = False
        
        # 出生日期检查
        birth_str = id_number[6:14]
        try:
            birth_date = datetime.strptime(birth_str, '%Y%m%d')
            # 检查日期合理性
            current_year = datetime.now().year
            if birth_date.year < 1900 or birth_date.year > current_year:
                return False, f"出生日期不合理：{birth_str}", metadata
            
            # 年龄不能为负数且不超过150岁
            age = (datetime.now() - birth_date).days // 365
            if age < 0 or age > 150:
                return False, f"年龄不合理：{age}岁", metadata
            
            metadata['birth_date'] = birth_date.strftime('%Y-%m-%d')
            metadata['age'] = age
        except ValueError:
            return False, f"出生日期无效：{birth_str}", metadata
        
        # 性别识别
        gender_code = int(id_number[16])
        metadata['gender'] = '男' if gender_code % 2 == 1 else '女'
        
        # 校验位计算
        total = sum(int(id_number[i]) * DetectionEngine.ID_CARD_WEIGHTS[i] for i in range(17))
        expected_check = DetectionEngine.ID_CARD_CHECK_CODES[total % 11]
        
        if id_number[17].upper() != expected_check:
            return False, f"校验位错误：期望{expected_check}，实际{id_number[17]}", metadata
        
        detail = f"有效身份证号，{metadata['area']}，{metadata['gender']}，{metadata['age']}岁"
        return True, detail, metadata
    
    @staticmethod
    def is_id_card(value: str) -> Tuple[bool, float, Dict[str, Any]]:
        """
        综合判断是否为身份证号
        
        Returns:
            (是否为身份证, 置信度, 元数据)
        """
        if not value:
            return False, 0.0, {}
        
        clean_value = value.strip().upper()
        
        # 18位身份证检查
        is_valid, detail, metadata = DetectionEngine.validate_id_card(clean_value)
        if is_valid:
            return True, 0.99, metadata
        
        # 可能是身份证但校验失败
        if re.match(r'^\d{17}[\dXx]$', clean_value):
            return False, 0.6, metadata
        
        # 15位旧版身份证（已停用，但历史数据可能存在）
        if re.match(r'^\d{15}$', clean_value):
            area_code = clean_value[:6]
            birth_str = '19' + clean_value[6:12]
            try:
                birth_date = datetime.strptime(birth_str, '%Y%m%d')
                age = (datetime.now() - birth_date).days // 365
                if 0 <= age <= 150:
                    metadata['area'] = DetectionEngine.ID_CARD_AREA_CODES.get(area_code, '未知地区')
                    metadata['birth_date'] = birth_date.strftime('%Y-%m-%d')
                    metadata['age'] = age
                    metadata['gender'] = '男' if int(clean_value[14]) % 2 == 1 else '女'
                    return True, 0.90, metadata
            except ValueError:
                pass
        
        return False, 0.0, {}
    
    @staticmethod
    def identify_bank_bin(card_number: str) -> Optional[Dict]:
        """
        根据BIN码识别银行
        
        Args:
            card_number: 银行卡号
            
        Returns:
            银行信息字典，或None
        """
        # 常见银行卡BIN码表
        BANK_BIN_MAP = {
            # 借记卡BIN
            "622908": {"bank": "兴业银行", "type": "借记卡"},
            "622909": {"bank": "兴业银行", "type": "借记卡"},
            "621700": {"bank": "建设银行", "type": "借记卡"},
            "621098": {"bank": "邮政储蓄银行", "type": "借记卡"},
            "622150": {"bank": "邮政储蓄银行", "type": "借记卡"},
            "622188": {"bank": "邮政储蓄银行", "type": "借记卡"},
            "621660": {"bank": "中国银行", "type": "借记卡"},
            "621661": {"bank": "中国银行", "type": "借记卡"},
            "622200": {"bank": "工商银行", "type": "借记卡"},
            "622202": {"bank": "工商银行", "type": "借记卡"},
            "622203": {"bank": "工商银行", "type": "借记卡"},
            "621226": {"bank": "工商银行", "type": "借记卡"},
            "622848": {"bank": "农业银行", "type": "借记卡"},
            "622845": {"bank": "农业银行", "type": "借记卡"},
            "622823": {"bank": "农业银行", "type": "借记卡"},
            "621058": {"bank": "平安银行", "type": "借记卡"},
            "622260": {"bank": "交通银行", "type": "借记卡"},
            "621030": {"bank": "北京银行", "type": "借记卡"},
            "621485": {"bank": "招商银行", "type": "借记卡"},
            "621486": {"bank": "招商银行", "type": "借记卡"},
            
            # 信用卡BIN
            "451289": {"bank": "兴业银行", "type": "信用卡"},
            "461982": {"bank": "兴业银行", "type": "信用卡"},
            "356889": {"bank": "招商银行", "type": "信用卡"},
            "439225": {"bank": "招商银行", "type": "信用卡"},
            "518710": {"bank": "招商银行", "type": "信用卡"},
            "427020": {"bank": "工商银行", "type": "信用卡"},
            "458060": {"bank": "工商银行", "type": "信用卡"},
            "530980": {"bank": "工商银行", "type": "信用卡"},
            "436742": {"bank": "建设银行", "type": "信用卡"},
            "436745": {"bank": "建设银行", "type": "信用卡"},
            "622700": {"bank": "建设银行", "type": "信用卡"},
        }
        
        if len(card_number) < 6:
            return None
        
        # 尝试匹配6位BIN
        bin_code = card_number[:6]
        if bin_code in BANK_BIN_MAP:
            return BANK_BIN_MAP[bin_code]
        
        # 尝试匹配5位BIN
        bin_code_5 = card_number[:5]
        for code, info in BANK_BIN_MAP.items():
            if code.startswith(bin_code_5):
                return info
        
        # 尝试匹配4位BIN
        bin_code_4 = card_number[:4]
        for code, info in BANK_BIN_MAP.items():
            if code.startswith(bin_code_4):
                return info
        
        return None
    
    def is_bank_card(self, card_number: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        综合判断是否为银行卡
        
        Args:
            card_number: 待识别的卡号字符串
            
        Returns:
            (是否为银行卡, 判断理由, 银行信息)
        """
        if not card_number:
            return False, "空字符串", None
        
        # 去除空格和横线
        clean_number = re.sub(r'[\s\-]', '', card_number)
        
        # 长度检查（银行卡通常是16-19位）
        if len(clean_number) < 16 or len(clean_number) > 19:
            return False, f"长度不符合银行卡特征（当前长度：{len(clean_number)}）", None
        
        # 纯数字检查
        if not clean_number.isdigit():
            return False, "包含非数字字符", None
        
        # BIN码识别
        bank_info = self.identify_bank_bin(clean_number)
        
        # Luhn校验
        if not self.luhn_check(clean_number):
            if bank_info:
                return False, "Luhn校验失败，可能是输入错误", bank_info
            return False, "Luhn校验失败", None
        
        # 综合判断
        if bank_info:
            return True, f"识别为{bank_info['bank']}{bank_info['type']}", bank_info
        else:
            # 即使BIN表没匹配，只要Luhn校验通过且长度合法，也可能是银行卡
            return True, "Luhn校验通过，疑似银行卡（BIN未在库中）", None
    
    def scan_text(self, text: str, column_name: str = "", row_index: int = 0, 
                  language: Optional[str] = None, selected_rules: Optional[List[int]] = None) -> List[DetectionMatch]:
        if not text or not isinstance(text, str):
            return []
        
        detected_lang = language or LanguageDetector.detect(text)[0]
        matches = []
        
        for rule in self.rules:
            if selected_rules and rule["id"] not in selected_rules:
                continue
            
            # 允许 "all" 语言的规则匹配任何检测到的语言
            if rule["language"] != "all" and rule["language"] != detected_lang and detected_lang != "unknown":
                continue
            
            rule_matches = self._apply_rule(text, rule, row_index, column_name, detected_lang)
            matches.extend(rule_matches)
        
        return matches
    
    def _apply_rule(self, text: str, rule: Dict, row_index: int, column_name: str, 
                    detected_lang: str) -> List[DetectionMatch]:
        matches = []
        
        # 预处理：检查文本是否像地址（长文本 + 地址关键词）
        is_likely_address = False
        if len(text) > 8:  # 地址通常比姓名长
            address_keywords = ['省', '市', '区', '县', '路', '街', '道', '号', '座', '栋', 
                              '小区', '村', '镇', '乡', '街道', '花园', '公寓', '大厦', '广场',
                              '광역시', '특별시', '구', '동', '리',
                              '県', '都', '府', '丁目', '番',
                              'rue', 'avenue', 'boulevard', 'street', 'road', 'straße']
            keyword_count = sum(1 for kw in address_keywords if kw.lower() in text.lower())
            has_number = bool(re.search(r'\d+', text))
            if keyword_count >= 2 or (keyword_count >= 1 and has_number):
                is_likely_address = True
        
        if rule["rule_type"] == "regex":
            # 跳过姓名正则规则，如果文本很可能是地址
            if rule["id"] in [3, 6, 9, 10, 11, 12]:  # 各种语言的姓名规则
                if is_likely_address:
                    return []  # 直接返回，不匹配姓名
                # 额外检查：姓名通常较短（<10个字符）
                if len(text.strip()) > 10:
                    return []
            
            compiled = rule.get("_compiled")
            if compiled:
                for m in compiled.finditer(text):
                    matched_text = m.group()
                    if len(matched_text) >= 2:
                        confidence = 0.85
                        rule_name = rule["name"]
                        
                        # 对于银行卡号规则，使用Luhn校验提高准确性
                        if rule["id"] == 4:  # 中国银行卡号
                            clean_number = re.sub(r'[\s\-]', '', matched_text)
                            if len(clean_number) >= 16 and len(clean_number) <= 19 and clean_number.isdigit():
                                if self.luhn_check(clean_number):
                                    confidence = 0.95  # Luhn校验通过，提高置信度
                                    bank_info = self.identify_bank_bin(clean_number)
                                    if bank_info:
                                        rule_name = f"{bank_info['bank']}{bank_info['type']}"
                                    else:
                                        rule_name = rule["name"]
                                else:
                                    # Luhn校验失败，跳过
                                    continue
                            else:
                                continue
                        
                        # 对于身份证号规则，使用完整校验逻辑
                        elif rule["id"] == 2:  # 中国大陆身份证
                            is_valid, id_confidence, metadata = self.is_id_card(matched_text)
                            if is_valid:
                                confidence = id_confidence  # 0.99
                                # 在规则名中添加详细信息
                                area = metadata.get('area', '未知地区')
                                gender = metadata.get('gender', '未知')
                                age = metadata.get('age', '?')
                                rule_name = f"身份证({area},{gender},{age}岁)"
                            else:
                                # 格式匹配但校验失败，降低置信度或跳过
                                if id_confidence > 0.5:
                                    confidence = id_confidence
                                else:
                                    continue
                        
                        matches.append(DetectionMatch(
                            row_index=row_index,
                            column_name=column_name,
                            detected_language=detected_lang,
                            rule_id=rule["id"],
                            rule_name=rule_name,
                            rule_type=rule["rule_type"],
                            matched_content=matched_text,
                            confidence=confidence,
                            desensitization_suggestion=rule.get("suggestion", "通用脱敏")
                        ))
        
        elif rule["rule_type"] == "keyword":
            keywords = rule.get("keywords", [])
            matched_keyword = None
            
            # 对于国家名称规则，使用精确匹配
            if rule["id"] == 31:  # 国家名称
                # 按长度降序排序，优先匹配长名称（如"United Kingdom"优于"UK"）
                sorted_keywords = sorted(keywords, key=len, reverse=True)
                for kw in sorted_keywords:
                    # 精确匹配整个文本或作为独立词出现
                    if text.strip() == kw or re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE):
                        matched_keyword = kw
                        break
            
            # 对于地址规则，使用AddressIdentifier进行智能识别
            elif rule["id"] in [5, 18, 21, 24, 27, 30]:  # 各种语言的地址规则
                # 对所有语言的地址都使用智能识别
                is_addr, addr_confidence, reason, address_info = AddressIdentifier.is_address(text)
                if is_addr and addr_confidence >= 0.3:  # 降低阈值到0.3
                    matched_keyword = True
                    confidence = addr_confidence
                    # 在规则名中添加地址结构信息
                    if address_info:
                        province = address_info.province or ''
                        city = address_info.city or ''
                        district = address_info.district or ''
                        if province and city and district:
                            rule_name = f"地址({province}{city}{district})"
                        elif province and city:
                            rule_name = f"地址({province}{city})"
                        else:
                            rule_name = rule["name"]
                    else:
                        rule_name = rule["name"]
                else:
                    # 回退到关键词匹配
                    keyword_count = sum(1 for kw in keywords if kw.lower() in text.lower())
                    has_number = bool(re.search(r'\d+', text))
                    # 降低关键词匹配要求：只要有1个关键词+数字，或2个关键词即可
                    if keyword_count >= 2 or (keyword_count >= 1 and has_number):
                        matched_keyword = True
                        confidence = max(0.6, confidence) if confidence else 0.6
            
            else:
                # 其他关键词规则：检查是否包含任意关键词
                for kw in keywords:
                    if kw.lower() in text.lower():
                        matched_keyword = kw
                        break
            
            if matched_keyword:
                # 根据规则类型调整置信度
                if rule["id"] == 31:  # 国家名称
                    confidence = 0.90
                elif rule["id"] in [5, 18, 21, 24, 27, 30]:  # 地址规则
                    # 如果之前已经设置了confidence（地址解析器），则保留
                    if 'confidence' not in locals() or confidence is None:
                        confidence = 0.80
                else:
                    confidence = 0.70
                
                matches.append(DetectionMatch(
                    row_index=row_index,
                    column_name=column_name,
                    detected_language=detected_lang,
                    rule_id=rule["id"],
                    rule_name=rule_name if 'rule_name' in locals() else rule["name"],
                    rule_type=rule["rule_type"],
                    matched_content=text[:100],
                    confidence=confidence,
                    desensitization_suggestion=rule.get("suggestion", "通用脱敏")
                ))
        
        return matches
    
    def scan_dataframe(self, df, columns: Optional[List[str]] = None, 
                       language_strategy: str = "auto",
                       selected_rules: Optional[List[int]] = None,
                       progress_callback=None) -> List[DetectionMatch]:
        import pandas as pd
        
        if columns:
            scan_cols = [c for c in columns if c in df.columns]
        else:
            scan_cols = list(df.columns)
        
        all_matches = []
        total_rows = len(df)
        
        for idx, row in df.iterrows():
            for col in scan_cols:
                value = str(row.get(col, ""))
                if not value or value == "nan":
                    continue
                
                lang = None
                if language_strategy == "auto":
                    lang = LanguageDetector.detect(value)[0]
                
                matches = self.scan_text(value, col, idx, lang, selected_rules)
                all_matches.extend(matches)
            
            if progress_callback and idx % 100 == 0:
                progress_callback(idx + 1, total_rows)
        
        if progress_callback:
            progress_callback(total_rows, total_rows)
        
        return all_matches
