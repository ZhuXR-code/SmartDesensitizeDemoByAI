import re
from typing import Tuple, Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, field


class AddressType(Enum):
    """地址类型枚举"""
    FULL_ADDRESS = "完整地址"  # 省市区街道详细地址
    PROVINCE_CITY = "省市地址"  # 只有省市
    CITY_DISTRICT = "市区地址"  # 只有市区
    DETAIL_ADDRESS = "详细地址"  # 街道门牌号等
    POBOX = "邮政信箱"  # 邮政信箱
    RURAL_ADDRESS = "农村地址"  # 包含村组的地址
    COMPANY_ADDRESS = "企业地址"  # 包含企业名称的地址
    UNKNOWN = "未知"


class AddressLevel(Enum):
    """地址级别"""
    COUNTRY = "国家"
    PROVINCE = "省级"  # 省/自治区/直辖市/特别行政区
    CITY = "地市级"  # 地级市/自治州/地区
    DISTRICT = "区县级"  # 市辖区/县级市/县/自治县
    STREET = "街道级"  # 街道/镇/乡
    COMMUNITY = "社区级"  # 社区/村/居委会
    BUILDING = "建筑级"  # 小区/大厦/楼栋
    ROOM = "房间级"  # 楼层/门牌号


@dataclass
class AddressInfo:
    """地址信息"""
    full_address: str  # 完整地址
    country: str = ""  # 国家
    province: str = ""  # 省/直辖市
    city: str = ""  # 地级市
    district: str = ""  # 区/县/县级市
    street: str = ""  # 街道/镇/乡
    community: str = ""  # 社区/村
    building: str = ""  # 小区/大厦/楼栋
    room: str = ""  # 门牌号/室
    detail: str = ""  # 其他详细描述
    postal_code: str = ""  # 邮政编码
    phone: str = ""  # 联系电话（从地址中提取）
    contact_person: str = ""  # 联系人（从地址中提取）

    # 识别信息
    confidence: float = 0.0  # 置信度
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


class AddressParser:
    """中国地址解析器"""

    # ==================== 行政区划数据（简化版，实际需要完整库） ====================

    # 省级行政区（34个）
    PROVINCES = {
        # 直辖市
        '北京': {'level': 'province', 'type': 'municipality', 'abbr': '京'},
        '天津': {'level': 'province', 'type': 'municipality', 'abbr': '津'},
        '上海': {'level': 'province', 'type': 'municipality', 'abbr': '沪'},
        '重庆': {'level': 'province', 'type': 'municipality', 'abbr': '渝'},
        # 省份
        '河北': {'level': 'province', 'type': 'province', 'abbr': '冀'},
        '山西': {'level': 'province', 'type': 'province', 'abbr': '晋'},
        '辽宁': {'level': 'province', 'type': 'province', 'abbr': '辽'},
        '吉林': {'level': 'province', 'type': 'province', 'abbr': '吉'},
        '黑龙江': {'level': 'province', 'type': 'province', 'abbr': '黑'},
        '江苏': {'level': 'province', 'type': 'province', 'abbr': '苏'},
        '浙江': {'level': 'province', 'type': 'province', 'abbr': '浙'},
        '安徽': {'level': 'province', 'type': 'province', 'abbr': '皖'},
        '福建': {'level': 'province', 'type': 'province', 'abbr': '闽'},
        '江西': {'level': 'province', 'type': 'province', 'abbr': '赣'},
        '山东': {'level': 'province', 'type': 'province', 'abbr': '鲁'},
        '河南': {'level': 'province', 'type': 'province', 'abbr': '豫'},
        '湖北': {'level': 'province', 'type': 'province', 'abbr': '鄂'},
        '湖南': {'level': 'province', 'type': 'province', 'abbr': '湘'},
        '广东': {'level': 'province', 'type': 'province', 'abbr': '粤'},
        '海南': {'level': 'province', 'type': 'province', 'abbr': '琼'},
        '四川': {'level': 'province', 'type': 'province', 'abbr': '川/蜀'},
        '贵州': {'level': 'province', 'type': 'province', 'abbr': '黔/贵'},
        '云南': {'level': 'province', 'type': 'province', 'abbr': '滇/云'},
        '陕西': {'level': 'province', 'type': 'province', 'abbr': '陕/秦'},
        '甘肃': {'level': 'province', 'type': 'province', 'abbr': '甘/陇'},
        '青海': {'level': 'province', 'type': 'province', 'abbr': '青'},
        '台湾': {'level': 'province', 'type': 'province', 'abbr': '台'},
        # 自治区
        '内蒙古': {'level': 'province', 'type': 'autonomous_region', 'abbr': '蒙'},
        '广西': {'level': 'province', 'type': 'autonomous_region', 'abbr': '桂'},
        '西藏': {'level': 'province', 'type': 'autonomous_region', 'abbr': '藏'},
        '宁夏': {'level': 'province', 'type': 'autonomous_region', 'abbr': '宁'},
        '新疆': {'level': 'province', 'type': 'autonomous_region', 'abbr': '新'},
        # 特别行政区
        '香港': {'level': 'province', 'type': 'sar', 'abbr': '港'},
        '澳门': {'level': 'province', 'type': 'sar', 'abbr': '澳'},
    }

    # 城市级别关键词
    CITY_KEYWORDS = [
        '市', '自治州', '地区', '盟'
    ]

    # 区县级关键词
    DISTRICT_KEYWORDS = [
        '区', '县', '自治县', '县级市', '旗', '自治旗', '特区', '林区'
    ]

    # 街道级关键词
    STREET_KEYWORDS = [
        '街道', '镇', '乡', '民族乡', '苏木', '民族苏木'
    ]

    # 社区村级关键词
    COMMUNITY_KEYWORDS = [
        '社区', '村', '嘎查', '居委会', '村委会'
    ]

    # 建筑级关键词
    BUILDING_KEYWORDS = [
        '小区', '花园', '公寓', '大厦', '大楼', '广场', '中心',
        '新村', '新邨', '家属院', '家属区', '宿舍', '大院', '苑',
        '楼', '栋', '幢', '座', '单元', '号院', '号院'
    ]

    # 道路关键词
    ROAD_KEYWORDS = [
        '路', '街', '道', '巷', '弄', '里', '胡同', '条',
        '大道', '大街', '大路', '公路', '环线', '环岛',
        '支路', '辅路', '便道'
    ]

    # 地址级别的后缀匹配模式
    ADDRESS_PATTERNS = {
        'province': re.compile(
            r'(北京|天津|上海|重庆|河北|山西|辽宁|吉林|黑龙江|'
            r'江苏|浙江|安徽|福建|江西|山东|河南|湖北|湖南|'
            r'广东|广西|海南|四川|贵州|云南|西藏|陕西|甘肃|'
            r'青海|宁夏|新疆|台湾|香港|澳门|'
            r'内蒙古)(?:省|市|自治区|特别行政区)?'
        ),
        'city': re.compile(
            r'[\u4e00-\u9fff]{2,6}(?:市|自治州|地区|盟)'
        ),
        'district': re.compile(
            r'[\u4e00-\u9fff]{2,6}(?:区|县|自治县|市|旗|自治旗|特区|林区)'
        ),
        'street': re.compile(
            r'[\u4e00-\u9fff]{2,6}(?:街道|镇|乡|民族乡|苏木|民族苏木)'
        ),
        'road': re.compile(
            r'[\u4e00-\u9fff]+(?:路|街|道|巷|弄|里|胡同|条|'
            r'大道|大街|大路|公路|环线|环岛)'
        ),
        'building': re.compile(
            r'[\u4e00-\u9fff0-9a-zA-Z]+(?:小区|花园|公寓|大厦|大楼|广场|中心|'
            r'新村|新邨|家属院|家属区|宿舍|大院|苑)'
        ),
        'room': re.compile(
            r'(?:[\u4e00-\u9fff]*?)(\d+)(?:号楼?|栋|幢|座|单元|层|楼|室|号|房间)'
        ),
        'postal_code': re.compile(
            r'\b(\d{6})\b'
        ),
        'phone': re.compile(
            r'(?:电话|Tel|tel|联系电话|手机|联系方式|联系人电话)[：:]*\s*'
            r'((?:\+?86)?1[3-9]\d{9})'
        ),
        'po_box': re.compile(
            r'(?:邮政信箱|信箱|P\.?O\.?\s*Box|邮箱)[：:]*\s*(\d+[A-Za-z]*)'
        ),
    }

    @classmethod
    def parse_address(cls, address_text: str) -> AddressInfo:
        """
        解析中国地址

        Args:
            address_text: 地址文本

        Returns:
            解析后的地址信息
        """
        if not address_text or not address_text.strip():
            return AddressInfo(full_address='', confidence=0.0)

        # 清理地址文本
        clean_address = cls._clean_address(address_text)

        info = AddressInfo(full_address=clean_address)

        # 逐步解析地址的各个部分
        cls._parse_province(clean_address, info)
        cls._parse_city(clean_address, info)
        cls._parse_district(clean_address, info)
        cls._parse_street_and_road(clean_address, info)
        cls._parse_community(clean_address, info)
        cls._parse_building_and_room(clean_address, info)
        cls._parse_postal_code(clean_address, info)
        cls._parse_phone_and_contact(clean_address, info)
        cls._parse_po_box(clean_address, info)

        # 提取其他详细信息
        cls._extract_detail(clean_address, info)

        # 计算置信度
        cls._calculate_confidence(info)

        # 确定地址类型
        cls._determine_address_type(info)

        return info

    @staticmethod
    def _clean_address(address: str) -> str:
        """清理地址文本"""
        # 去除多余空格
        address = re.sub(r'\s+', ' ', address.strip())
        # 统一标点符号
        address = address.replace('，', ',').replace('；', ';').replace('：', ':')
        # 去除特殊字符（保留中英文、数字、常用标点）
        address = re.sub(r'[^\u4e00-\u9fff\w\s,;:.\-()（）#号栋幢座单元层楼室]', '', address)
        return address

    @classmethod
    def _parse_province(cls, address: str, info: AddressInfo):
        """解析省级行政区"""
        match = cls.ADDRESS_PATTERNS['province'].search(address)
        if match:
            province_name = match.group(1)
            # 补全省份全称
            if province_name in cls.PROVINCES:
                info.province = province_name
                if cls.PROVINCES[province_name]['type'] == 'municipality':
                    # 直辖市，城市名称就是省份名称
                    info.city = province_name

    @classmethod
    def _parse_city(cls, address: str, info: AddressInfo):
        """解析城市"""
        match = cls.ADDRESS_PATTERNS['city'].search(address)
        if match:
            city_name = match.group()
            if info.city and city_name == info.city:
                return
            # 排除与省份重复的匹配
            if info.province and city_name == info.province + '市':
                return
            info.city = city_name.rstrip('市自治州地区盟')

    @classmethod
    def _parse_district(cls, address: str, info: AddressInfo):
        """解析区县"""
        match = cls.ADDRESS_PATTERNS['district'].search(address)
        if match:
            district_name = match.group()
            # 排除与城市重复的匹配
            if info.city and district_name == info.city + '区':
                return
            info.district = district_name.rstrip('区县自治县市旗自治旗特区林区')

    @classmethod
    def _parse_street_and_road(cls, address: str, info: AddressInfo):
        """解析街道和道路"""
        # 解析街道
        street_match = cls.ADDRESS_PATTERNS['street'].search(address)
        if street_match:
            info.street = street_match.group()

        # 解析道路
        road_matches = cls.ADDRESS_PATTERNS['road'].findall(address)
        if road_matches:
            # 保留不重复的道路名
            info.detail = ' '.join(road_matches[:3])  # 最多保留3条道路

    @classmethod
    def _parse_community(cls, address: str, info: AddressInfo):
        """解析社区/村"""
        for keyword in cls.COMMUNITY_KEYWORDS:
            pattern = re.compile(rf'[\u4e00-\u9fff0-9]+{keyword}')
            match = pattern.search(address)
            if match:
                info.community = match.group()
                break

    @classmethod
    def _parse_building_and_room(cls, address: str, info: AddressInfo):
        """解析建筑和房间号"""
        # 解析小区/大厦
        building_match = cls.ADDRESS_PATTERNS['building'].search(address)
        if building_match:
            info.building = building_match.group()

        # 解析门牌号/室
        room_matches = cls.ADDRESS_PATTERNS['room'].findall(address)
        if room_matches:
            # 构建门牌号描述
            room_parts = []
            for match in cls.ADDRESS_PATTERNS['room'].finditer(address):
                room_parts.append(match.group())
            info.room = ' '.join(room_parts[-3:])  # 保留最后3个

    @classmethod
    def _parse_postal_code(cls, address: str, info: AddressInfo):
        """解析邮政编码"""
        match = cls.ADDRESS_PATTERNS['postal_code'].search(address)
        if match:
            info.postal_code = match.group(1)

    @classmethod
    def _parse_phone_and_contact(cls, address: str, info: AddressInfo):
        """解析联系电话和联系人"""
        # 解析电话
        phone_match = cls.ADDRESS_PATTERNS['phone'].search(address)
        if phone_match:
            info.phone = phone_match.group(1)

        # 解析联系人（简单规则：在电话前的姓名）
        if info.phone:
            phone_pos = address.find(info.phone)
            before_phone = address[:phone_pos]
            contact_match = re.search(r'收件人[：:]*\s*([\u4e00-\u9fff]{2,4})', before_phone)
            if contact_match:
                info.contact_person = contact_match.group(1)

    @classmethod
    def _parse_po_box(cls, address: str, info: AddressInfo):
        """解析邮政信箱"""
        match = cls.ADDRESS_PATTERNS['po_box'].search(address)
        if match:
            info.detail = f"邮政信箱 {match.group(1)}"
            info.address_type = AddressType.POBOX

    @classmethod
    def _extract_detail(cls, address: str, info: AddressInfo):
        """提取其他详细信息"""
        # 移除已解析的部分
        remaining = address
        for part in [info.province, info.city, info.district,
                     info.street, info.community, info.building, info.room,
                     info.postal_code, info.phone]:
            if part:
                remaining = remaining.replace(part, '', 1)

        # 清理剩余文本
        remaining = re.sub(r'\s+', ' ', remaining).strip()
        remaining = re.sub(r'[,;:.\-()（）#]+', ' ', remaining).strip()

        if remaining and remaining != info.detail:
            if info.detail:
                info.detail = remaining + ' ' + info.detail
            else:
                info.detail = remaining

    @classmethod
    def _calculate_confidence(cls, info: AddressInfo):
        """计算地址识别的置信度"""
        score = 0
        weights = {
            'province': 25,
            'city': 20,
            'district': 15,
            'street': 10,
            'community': 8,
            'building': 8,
            'room': 6,
            'postal_code': 5,
            'phone': 3
        }

        for field, weight in weights.items():
            if getattr(info, field):
                score += weight

        info.confidence = min(score / 100, 1.0)

        # 确定解析到的级别
        if info.room:
            info.parsed_level = AddressLevel.ROOM
        elif info.building:
            info.parsed_level = AddressLevel.BUILDING
        elif info.community:
            info.parsed_level = AddressLevel.COMMUNITY
        elif info.street:
            info.parsed_level = AddressLevel.STREET
        elif info.district:
            info.parsed_level = AddressLevel.DISTRICT
        elif info.city:
            info.parsed_level = AddressLevel.CITY
        elif info.province:
            info.parsed_level = AddressLevel.PROVINCE

    @classmethod
    def _determine_address_type(cls, info: AddressInfo):
        """确定地址类型"""
        if info.address_type == AddressType.POBOX:
            return

        if info.province and info.city and info.district and info.street:
            info.address_type = AddressType.FULL_ADDRESS
        elif info.province and info.city:
            info.address_type = AddressType.PROVINCE_CITY
        elif info.city and info.district:
            info.address_type = AddressType.CITY_DISTRICT
        elif info.building or info.room:
            info.address_type = AddressType.DETAIL_ADDRESS

        # 检查是否为农村地址
        if info.community and ('村' in info.community or '乡' in info.street):
            info.address_type = AddressType.RURAL_ADDRESS


class AddressIdentifier:
    """地址识别器（判断给定文本是否为地址）"""

    # 地址特征关键词
    ADDRESS_KEYWORDS = {
        'administrative': [
            '省', '市', '区', '县', '自治州', '自治县', '旗', '自治旗',
            '街道', '镇', '乡', '村', '社区', '居委会', '村委会', '嘎查',
            '苏木', '民族乡', '民族苏木', '特区', '林区', '地区', '盟'
        ],
        'road': [
            '路', '街', '道', '巷', '弄', '里', '胡同', '条',
            '大道', '大街', '大路', '公路', '环线', '环岛',
            '支路', '辅路', '便道', '高速', '国道', '省道'
        ],
        'building': [
            '小区', '花园', '公寓', '大厦', '大楼', '广场', '中心',
            '新村', '新邨', '家属院', '家属区', '宿舍', '大院', '苑',
            '号楼', '栋', '幢', '座', '单元', '号院', '排', '号'
        ],
        'number': [
            '号', '门', '室', '层', '楼', '单元', '房间',
            '门牌', '牌号', '门面'
        ],
        'direction': [
            '东', '南', '西', '北', '中', '内', '外',
            '前', '后', '左', '右', '东南', '西南', '东北', '西北'
        ]
    }

    # 非地址模式（帮助排除误判）
    NON_ADDRESS_PATTERNS = [
        r'^\d{17}[\dXx]$',  # 身份证号
        r'^1[3-9]\d{9}$',  # 手机号
        r'^\d{3,4}-\d{7,8}$',  # 固定电话
        r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$',  # 邮箱
        r'^\d{16,19}$',  # 银行卡号
        r'^\d{6}$',  # 纯6位数字（可能是邮编）
        r'^[A-Z]+\d+$',  # 护照号模式
    ]

    @classmethod
    def is_address(cls, text: str) -> Tuple[bool, float, str, Optional[AddressInfo]]:
        """
        判断给定文本是否为地址

        Args:
            text: 待识别的文本

        Returns:
            (是否为地址, 置信度, 理由, 地址解析信息)
        """
        if not text or not text.strip():
            return False, 0.0, "空文本", None

        clean_text = text.strip()

        # 1. 长度检查
        if len(clean_text) < 4:
            return False, 0.0, "文本过短，不可能是地址", None

        if len(clean_text) > 200:
            return False, 0.3, "文本过长，可能是描述性文本而非地址", None

        # 2. 排除明显的非地址模式
        for pattern in cls.NON_ADDRESS_PATTERNS:
            if re.match(pattern, clean_text):
                return False, 0.0, f"匹配非地址模式", None

        # 3. 特征词统计
        feature_score = cls._calculate_feature_score(clean_text)

        # 4. 中文比例检查
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', clean_text))
        total_chars = len(clean_text.replace(' ', ''))
        chinese_ratio = chinese_chars / max(total_chars, 1)

        if chinese_ratio < 0.3:
            return False, 0.1, "中文字符比例过低", None

        # 5. 地址解析
        address_info = AddressParser.parse_address(clean_text)

        # 6. 综合判断
        confidence = 0.0
        reasons = []

        # 地址解析置信度
        if address_info.confidence > 0.3:
            confidence += address_info.confidence * 0.6
            reasons.append(f"解析到{address_info.parsed_level.value}")

        # 特征词得分
        if feature_score > 2:
            confidence += min(feature_score / 10, 0.4)
            reasons.append(f"地址特征词得分: {feature_score:.1f}")

        # 结构特征
        if address_info.province and (address_info.city or address_info.district):
            confidence += 0.2
            reasons.append("包含省市结构")

        if address_info.building or address_info.room:
            confidence += 0.15
            reasons.append("包含建筑/门牌信息")

        confidence = min(confidence, 1.0)

        if confidence > 0.5:
            return True, confidence, '; '.join(reasons), address_info
        elif confidence > 0.3:
            return True, confidence, f"疑似地址，置信度较低; {'; '.join(reasons)}", address_info
        else:
            return False, confidence, f"不像是地址; {'; '.join(reasons)}", None

    @classmethod
    def _calculate_feature_score(cls, text: str) -> float:
        """计算地址特征得分"""
        score = 0.0

        for category, keywords in cls.ADDRESS_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    # 行政区划词权重更高
                    if category == 'administrative':
                        score += 0.8
                    elif category == 'road':
                        score += 0.6
                    elif category == 'building':
                        score += 0.5
                    elif category == 'number':
                        score += 0.3
                    elif category == 'direction':
                        score += 0.2

        return score

    @classmethod
    def is_address_simple(cls, text: str) -> bool:
        """简化的地址判断（只返回布尔值）"""
        is_addr, _, _, _ = cls.is_address(text)
        return is_addr

    @classmethod
    def extract_address_from_text(cls, text: str) -> List[AddressInfo]:
        """
        从一段文本中提取所有可能的地址

        Args:
            text: 包含地址的文本

        Returns:
            地址信息列表
        """
        addresses = []

        # 使用句号、分号、换行等分割文本
        sentences = re.split(r'[。；;.\n]', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            is_addr, confidence, _, address_info = cls.is_address(sentence)
            if is_addr and confidence > 0.5:
                if address_info:
                    addresses.append(address_info)

        return addresses


# ==================== 集成到数据类型识别系统 ====================

class DataTypeIdentifierExtended(DataTypeIdentifier):
    """扩展的数据类型识别器，包含地址识别"""

    @classmethod
    def identify_data_type(cls, value: str) -> IdentificationResult:
        """
        综合识别数据类型

        按优先级尝试各种识别器
        """
        if not value or not value.strip():
            return IdentificationResult(DataType.UNKNOWN, CountryCode.UNKNOWN, 0.0)

        clean_value = value.strip()

        # 1. 身份证号检查
        result = cls.is_id_card(clean_value)
        if result.confidence > 0.9:
            return result

        # 2. 银行卡号检查
        result = cls.is_bank_card(clean_value)  # 假设已实现
        if result.confidence > 0.9:
            return result

        # 3. 手机号检查
        result = cls.is_phone_number(clean_value)  # 假设已实现
        if result.confidence > 0.9:
            return result

        # 4. 邮箱检查
        result = cls.is_email(clean_value)  # 假设已实现
        if result.confidence > 0.9:
            return result

        # 5. 护照号检查
        result = cls.is_passport(clean_value)
        if result.confidence > 0.9:
            return result

        # 6. 统一社会信用代码检查
        result = cls.is_social_credit_code(clean_value)
        if result.confidence > 0.9:
            return result

        # 7. 地址检查
        is_addr, confidence, reason, address_info = AddressIdentifier.is_address(clean_value)
        if is_addr and confidence > 0.5:
            return IdentificationResult(
                DataType.ADDRESS,
                CountryCode.CN,
                confidence,
                reason,
                address_info.to_dict() if address_info else {}
            )

        # 8. 默认返回未知
        return IdentificationResult(DataType.UNKNOWN, CountryCode.UNKNOWN, 0.0)


# ==================== 测试函数 ====================

def test_address_identification():
    """测试地址识别功能"""

    print("=" * 70)
    print("地址识别测试")
    print("=" * 70)

    # 测试用例
    test_cases = [
        # 标准完整地址
        "北京市东城区东长安街1号东方广场C1座1201室",
        "上海市浦东新区陆家嘴环路1000号恒生银行大厦18楼",
        "广东省深圳市南山区科技园南路深圳湾科技生态园9栋B座5层",
        "浙江省杭州市西湖区文三路478号华星时代广场A座",
        "四川省成都市武侯区天府大道中段688号大源国际中心",

        # 简化地址
        "深圳市宝安区西乡街道固戍社区宝安大道5010号",
        "广州市天河区体育西路191号中石化大厦",
        "南京市玄武区中山路18号德基广场",

        # 包含联系方式的地址
        "北京市海淀区中关村大街1号海龙大厦，联系电话：13800138000",
        "收件人张三，上海市黄浦区南京东路100号，电话13912345678",

        # 农村地址
        "浙江省绍兴市柯桥区杨汛桥镇竹园童村",
        "河北省石家庄市正定县南牛乡东杨庄村",

        # 非地址文本
        "张三",
        "13800138000",
        "110101199001011234",
        "622908617822214081",
        "zhangsan@example.com",

        # 边界情况
        "建设路15号",
        "北京市朝阳区",
        "中关村",
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─' * 60}")
        print(f"测试 {i}: {test_case}")

        is_addr, confidence, reason, address_info = AddressIdentifier.is_address(test_case)

        print(f"  是否为地址: {'是' if is_addr else '否'}")
        print(f"  置信度: {confidence:.2%}")
        print(f"  理由: {reason}")

        if address_info and is_addr:
            print(f"  解析结果:")
            print(f"    省份: {address_info.province or '未识别'}")
            print(f"    城市: {address_info.city or '未识别'}")
            print(f"    区县: {address_info.district or '未识别'}")
            print(f"    街道: {address_info.street or '未识别'}")
            print(f"    社区/村: {address_info.community or '未识别'}")
            print(f"    建筑: {address_info.building or '未识别'}")
            print(f"    门牌号: {address_info.room or '未识别'}")
            print(f"    邮编: {address_info.postal_code or '未识别'}")
            print(f"    电话: {address_info.phone or '未识别'}")
            print(f"    联系人: {address_info.contact_person or '未识别'}")
            print(f"    地址类型: {address_info.address_type.value}")
            print(f"    解析级别: {address_info.parsed_level.value}")


def test_address_parsing():
    """测试地址解析详细功能"""

    print("\n" + "=" * 70)
    print("地址解析详细测试")
    print("=" * 70)

    test_addresses = [
        ("完整商业地址",
         "广东省深圳市南山区粤海街道科技园社区高新南一道009号中国科技开发院3号楼5层502室"),
        ("包含邮编的地址",
         "北京市西城区金融街7号英蓝国际金融中心，100033"),
        ("住宅地址",
         "上海市浦东新区花木街道锦绣路300弄35号901室"),
        ("大学地址",
         "北京市海淀区颐和园路5号北京大学"),
        ("工业园区地址",
         "江苏省苏州市工业园区星湖街328号创意产业园A1栋2层"),
    ]

    for name, address in test_addresses:
        print(f"\n{'─' * 60}")
        print(f"【{name}】")
        print(f"原文: {address}")

        info = AddressParser.parse_address(address)
        print(f"解析结果: {info.to_dict()}")
        print(f"置信度: {info.confidence:.2%}")
        print(f"地址类型: {info.address_type.value}")


def test_address_extraction():
    """测试从文本中提取地址"""

    print("\n" + "=" * 70)
    print("从文本中提取地址测试")
    print("=" * 70)

    # 模拟一段包含多个地址的文本
    text = """
    张三，身份证号110101199001011234，现住北京市海淀区中关村大街1号海龙大厦1201室。
    李四的工作单位是上海市浦东新区陆家嘴环路1000号恒生银行大厦18楼，手机号13800138000。
    王五的户籍地址是广东省深圳市南山区科技园南路深圳湾科技生态园9栋B座5层。
    """

    addresses = AddressIdentifier.extract_address_from_text(text)

    print(f"原文:\n{text}")
    print(f"\n提取到 {len(addresses)} 个地址:")

    for i, addr in enumerate(addresses, 1):
        print(f"\n地址 {i}:")
        print(f"  {addr.full_address}")
        print(f"  置信度: {addr.confidence:.2%}")
        print(f"  类型: {addr.address_type.value}")
        print(f"  解析级别: {addr.parsed_level.value}")


if __name__ == "__main__":
    test_address_identification()
    test_address_parsing()
    test_address_extraction()