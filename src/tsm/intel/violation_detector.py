"""Violation pattern detection for tobacco-related crimes.

This module provides intelligent detection algorithms for the five major
violation patterns identified in tobacco law enforcement:
- Door-to-Door Sales (上门推销)
- Dedicated Vehicle Transport (专车运输)
- Logistics Delivery (物流配送)
- Maritime Smuggling (海上走私)
- Counterfeit Production Sites (假烟制售点)

Each pattern detector analyzes article content and extracts structured
intelligence with confidence scores and supporting evidence.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from tsm.intel.entity_extractor import CaseEntities, extract_entities


class ViolationPattern(str, Enum):
    """Types of violation patterns."""
    DOOR_TO_DOOR = "door_to_door"  # 上门推销
    VEHICLE_TRANSPORT = "vehicle_transport"  # 专车运输
    LOGISTICS_DELIVERY = "logistics_delivery"  # 物流配送
    MARITIME_SMUGGLING = "maritime_smuggling"  # 海上走私
    COUNTERFEIT_SITE = "counterfeit_site"  # 假烟制售点
    UNKNOWN = "unknown"  # 未知模式


@dataclass
class PatternMatch:
    """Represents a detected pattern match in text."""
    pattern_type: ViolationPattern
    confidence: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)  # Supporting text snippets
    keywords_matched: List[str] = field(default_factory=list)  # Keywords that triggered detection
    details: Dict[str, any] = field(default_factory=dict)  # Additional extracted details


@dataclass
class ViolationAnalysis:
    """Complete analysis result for an article."""
    primary_pattern: ViolationPattern
    primary_confidence: float
    all_patterns: List[PatternMatch] = field(default_factory=list)
    entities: Optional[CaseEntities] = None
    risk_factors: List[str] = field(default_factory=list)  # Additional risk indicators
    geographic_hints: List[str] = field(default_factory=list)  # Location clues
    temporal_hints: List[str] = field(default_factory=list)  # Time clues


# ============================================================================
# Pattern Detection Rules
# ============================================================================

# Door-to-Door Sales Keywords (上门推销)
DOOR_TO_DOOR_KEYWORDS = {
    # Direct indicators (high confidence)
    "high": [
        "上门推销", "上门销售", "入户推销", "走街串巷", "上门送货",
        "社区推销", "小区推销", "村民推销", "农村推销",
        "上门兜售", "上门叫卖", "挨家挨户", "上门销售烟",
    ],
    # Contextual indicators (medium confidence)
    "medium": [
        "流动销售", "流动摊点", "无固定场所", "流动兜售",
        "面对面交易", "现场交易", "现金交易", "微信销售",
        "朋友圈卖烟", "私下交易", "个人销售",
    ],
    # Supporting context (low confidence)
    "low": [
        "香烟", "烟草", "卷烟", "假烟", "走私烟",
        "便宜", "低价", "折扣", "优惠",
    ],
}

# Vehicle Transport Keywords (专车运输)
VEHICLE_TRANSPORT_KEYWORDS = {
    "high": [
        "专车运输", "专用车辆", "运输车辆", "货车运输",
        "跨省运输", "长途运输", "非法运输烟草",
        "无证运输烟草", "无准运证", "无烟草专卖品准运证",
        "非法运输卷烟", "车辆运输烟草", "运输假烟",
    ],
    "medium": [
        "货车查获", "面包车运输", "厢式货车", "运输途中",
        "高速路口查获", "检查站查获", "设卡检查",
        "车牌号", "车辆信息", "驾驶员",
        "运输路线", "运输网络", "运输渠道",
    ],
    "low": [
        "运输", "车辆", "司机", "货物",
        "高速", "国道", "省道", "收费站",
    ],
}

# Logistics Delivery Keywords (物流配送)
LOGISTICS_DELIVERY_KEYWORDS = {
    "high": [
        "物流配送", "快递运输", "邮寄烟草", "快递寄递",
        "物流发货", "快递发货", "邮寄假烟",
        "非法邮寄烟草", "快递渠道", "物流渠道",
        "假烟快递", "走私烟快递", "网购烟草",
    ],
    "medium": [
        "快递单号", "物流单号", "运单号", "收件人", "寄件人",
        "快递包裹", "物流包裹", "包装箱",
        "电商平台销售", "网上销售", "网络销售烟草",
        "代购烟草", "微商卖烟",
    ],
    "low": [
        "快递", "物流", "邮寄", "配送", "发货",
        "收货", "签收", "派送",
    ],
}

# Maritime Smuggling Keywords (海上走私)
MARITIME_SMUGGLING_KEYWORDS = {
    "high": [
        "海上走私", "走私烟草", "走私卷烟", "海上偷运",
        "走私船", "渔船走私", "货船走私", "快艇走私",
        "海上拦截", "海警查获", "海关缉私",
        "境外走私烟草", "跨境走私", "走私入境",
        "非设关地走私", "沿海走私", "码头走私",
    ],
    "medium": [
        "港口查获", "码头查获", "船舶运输", "海运",
        "边防检查", "出入境检查", "海关检查",
        "境外烟草", "外国烟", "洋烟",
        "免税烟走私", "走私香烟",
        "南海", "东海", "黄海", "渤海",
    ],
    "low": [
        "港口", "码头", "船舶", "渔船", "货轮",
        "海关", "边防", "出入境",
    ],
}

# Counterfeit Production Site Keywords (假烟制售点)
COUNTERFEIT_SITE_KEYWORDS = {
    "high": [
        "制假窝点", "造假窝点", "制售假烟", "生产假烟",
        "假冒卷烟生产", "假烟工厂", "黑工厂",
        "制假售假", "制假基地", "造假基地",
        "印刷假商标", "假冒商标", "非法生产烟草",
        "地下工厂", "黑作坊", "家庭作坊制烟",
    ],
    "medium": [
        "生产设备", "制烟设备", "卷烟机", "包装机",
        "假冒品牌", "仿冒商标", "假冒包装",
        "原材料仓库", "烟叶存储", "辅料存储",
        "窝藏假烟", "存储假烟", "假烟仓库",
        "生产用电异常", "用电量激增",
    ],
    "low": [
        "生产", "制造", "加工", "包装", "存储",
        "仓库", "厂房", "车间",
    ],
}


def _count_keyword_matches(text: str, keyword_dict: Dict[str, List[str]]) -> Tuple[int, int, int, List[str]]:
    """Count keyword matches at each confidence level.
    
    Returns:
        Tuple of (high_count, medium_count, low_count, all_matched_keywords)
    """
    high_count = 0
    medium_count = 0
    low_count = 0
    matched = []
    
    for kw in keyword_dict.get("high", []):
        if kw in text:
            high_count += 1
            matched.append(kw)
    
    for kw in keyword_dict.get("medium", []):
        if kw in text:
            medium_count += 1
            matched.append(kw)
    
    for kw in keyword_dict.get("low", []):
        if kw in text:
            low_count += 1
            matched.append(kw)
    
    return high_count, medium_count, low_count, matched


def _calculate_confidence(high: int, medium: int, low: int) -> float:
    """Calculate confidence score based on keyword matches.
    
    Weighted scoring:
    - High confidence keywords: weight 3
    - Medium confidence keywords: weight 2
    - Low confidence keywords: weight 1
    
    Confidence caps at 1.0
    """
    score = high * 3 + medium * 2 + low * 1
    # Normalize to 0.0-1.0 range
    # Need at least 1 high or 2 medium keywords for moderate confidence
    # 3+ high keywords = max confidence
    if score >= 9:
        return 1.0
    elif score >= 6:
        return 0.8
    elif score >= 4:
        return 0.6
    elif score >= 2:
        return 0.4
    elif score >= 1:
        return 0.2
    return 0.0


def _extract_evidence(text: str, keywords: List[str], context_chars: int = 30) -> List[str]:
    """Extract text snippets around matched keywords for evidence.
    
    Args:
        text: Full article text
        keywords: Keywords that were matched
        context_chars: Characters to include before/after match
        
    Returns:
        List of evidence snippets
    """
    evidence = []
    for kw in keywords:
        idx = text.find(kw)
        if idx != -1:
            start = max(0, idx - context_chars)
            end = min(len(text), idx + len(kw) + context_chars)
            snippet = text[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(text):
                snippet = snippet + "..."
            if snippet not in evidence:
                evidence.append(snippet)
    return evidence[:5]  # Limit to 5 evidence snippets


def detect_door_to_door(text: str) -> PatternMatch:
    """Detect door-to-door sales pattern.
    
    上门推销：监控社交媒体、本地论坛、社区群组中的可疑烟草销售活动
    """
    high, medium, low, matched = _count_keyword_matches(text, DOOR_TO_DOOR_KEYWORDS)
    confidence = _calculate_confidence(high, medium, low)
    evidence = _extract_evidence(text, matched)
    
    # Additional indicators
    details = {}
    
    # Check for social media sales patterns
    social_patterns = ["微信", "朋友圈", "QQ群", "微信群", "抖音", "快手", "小红书"]
    social_matches = [p for p in social_patterns if p in text]
    if social_matches:
        details["social_platforms"] = social_matches
        confidence = min(1.0, confidence + 0.1)
    
    # Check for pricing indicators
    price_patterns = ["元/条", "元一条", "便宜", "特价", "批发价", "零售价"]
    price_matches = [p for p in price_patterns if p in text]
    if price_matches:
        details["price_indicators"] = price_matches
    
    return PatternMatch(
        pattern_type=ViolationPattern.DOOR_TO_DOOR,
        confidence=confidence,
        evidence=evidence,
        keywords_matched=matched,
        details=details
    )


def detect_vehicle_transport(text: str, entities: Optional[CaseEntities] = None) -> PatternMatch:
    """Detect dedicated vehicle transport pattern.
    
    专车运输：分析GPS轨迹和车辆移动模式（从文本中提取线索）
    """
    high, medium, low, matched = _count_keyword_matches(text, VEHICLE_TRANSPORT_KEYWORDS)
    confidence = _calculate_confidence(high, medium, low)
    evidence = _extract_evidence(text, matched)
    
    details = {}
    
    # Check for cross-region indicators
    cross_region = ["跨省", "跨市", "跨区", "省际", "市际", "跨区域"]
    cross_matches = [c for c in cross_region if c in text]
    if cross_matches:
        details["cross_region"] = True
        details["cross_region_indicators"] = cross_matches
        confidence = min(1.0, confidence + 0.15)
    
    # Check for route information
    route_patterns = ["高速", "国道", "省道", "收费站", "检查站", "服务区"]
    route_matches = [r for r in route_patterns if r in text]
    if route_matches:
        details["route_indicators"] = route_matches
    
    # Use extracted vehicle info if available
    if entities and entities.vehicle_info:
        details["vehicle_info"] = entities.vehicle_info
        confidence = min(1.0, confidence + 0.1)
    
    return PatternMatch(
        pattern_type=ViolationPattern.VEHICLE_TRANSPORT,
        confidence=confidence,
        evidence=evidence,
        keywords_matched=matched,
        details=details
    )


def detect_logistics_delivery(text: str) -> PatternMatch:
    """Detect logistics/delivery pattern.
    
    物流配送：追踪包裹发货，检测可疑的烟草相关配送
    """
    high, medium, low, matched = _count_keyword_matches(text, LOGISTICS_DELIVERY_KEYWORDS)
    confidence = _calculate_confidence(high, medium, low)
    evidence = _extract_evidence(text, matched)
    
    details = {}
    
    # Check for e-commerce platform mentions
    platforms = ["淘宝", "天猫", "京东", "拼多多", "闲鱼", "1688", "微店"]
    platform_matches = [p for p in platforms if p in text]
    if platform_matches:
        details["ecommerce_platforms"] = platform_matches
        confidence = min(1.0, confidence + 0.1)
    
    # Check for logistics company mentions
    logistics = ["顺丰", "圆通", "中通", "申通", "韵达", "邮政", "EMS", "京东物流", "菜鸟"]
    logistics_matches = [l for l in logistics if l in text]
    if logistics_matches:
        details["logistics_companies"] = logistics_matches
    
    # Check for online transaction indicators
    transaction = ["支付宝", "微信支付", "银行转账", "货到付款", "在线支付"]
    transaction_matches = [t for t in transaction if t in text]
    if transaction_matches:
        details["payment_methods"] = transaction_matches
    
    return PatternMatch(
        pattern_type=ViolationPattern.LOGISTICS_DELIVERY,
        confidence=confidence,
        evidence=evidence,
        keywords_matched=matched,
        details=details
    )


def detect_maritime_smuggling(text: str) -> PatternMatch:
    """Detect maritime smuggling pattern.
    
    海上走私：监控AIS船舶数据和港口活动（从文本中提取线索）
    """
    high, medium, low, matched = _count_keyword_matches(text, MARITIME_SMUGGLING_KEYWORDS)
    confidence = _calculate_confidence(high, medium, low)
    evidence = _extract_evidence(text, matched)
    
    details = {}
    
    # Check for port/harbor mentions
    ports = ["港口", "码头", "泊位", "锚地", "港区", "海关监管区"]
    port_matches = [p for p in ports if p in text]
    if port_matches:
        details["port_indicators"] = port_matches
    
    # Check for coastal region mentions
    coastal_regions = [
        "广东", "福建", "浙江", "江苏", "山东", "辽宁", "广西", "海南",
        "深圳", "珠海", "汕头", "厦门", "宁波", "青岛", "大连", "北海"
    ]
    region_matches = [r for r in coastal_regions if r in text]
    if region_matches:
        details["coastal_regions"] = region_matches
        confidence = min(1.0, confidence + 0.1)
    
    # Check for international trade indicators
    international = ["境外", "国外", "进口", "走私入境", "偷运入境", "边境"]
    intl_matches = [i for i in international if i in text]
    if intl_matches:
        details["international_indicators"] = intl_matches
        confidence = min(1.0, confidence + 0.1)
    
    # Check for maritime enforcement
    enforcement = ["海警", "海关", "边防", "缉私", "海事"]
    enforcement_matches = [e for e in enforcement if e in text]
    if enforcement_matches:
        details["enforcement_agencies"] = enforcement_matches
    
    return PatternMatch(
        pattern_type=ViolationPattern.MARITIME_SMUGGLING,
        confidence=confidence,
        evidence=evidence,
        keywords_matched=matched,
        details=details
    )


def detect_counterfeit_site(text: str, entities: Optional[CaseEntities] = None) -> PatternMatch:
    """Detect counterfeit production site pattern.
    
    假烟制售点：通过工商注册异常和用电量模式检测假生产点
    """
    high, medium, low, matched = _count_keyword_matches(text, COUNTERFEIT_SITE_KEYWORDS)
    confidence = _calculate_confidence(high, medium, low)
    evidence = _extract_evidence(text, matched)
    
    details = {}
    
    # Check for equipment mentions
    equipment = ["卷烟机", "包装机", "切丝机", "烘干设备", "生产设备", "机器设备"]
    equipment_matches = [e for e in equipment if e in text]
    if equipment_matches:
        details["equipment_indicators"] = equipment_matches
        confidence = min(1.0, confidence + 0.1)
    
    # Check for raw material mentions
    materials = ["烟叶", "烟丝", "卷烟纸", "滤嘴", "包装材料", "商标"]
    material_matches = [m for m in materials if m in text]
    if material_matches:
        details["material_indicators"] = material_matches
    
    # Check for location characteristics
    location_types = ["出租屋", "民房", "地下室", "仓库", "废弃厂房", "偏僻"]
    location_matches = [l for l in location_types if l in text]
    if location_matches:
        details["location_types"] = location_matches
    
    # Use extracted brand info if available
    if entities and entities.brands:
        details["counterfeit_brands"] = entities.brands
        confidence = min(1.0, confidence + 0.05)
    
    # Check for quantity/production scale
    if entities and entities.quantity_value:
        details["production_scale"] = {
            "quantity": entities.quantity,
            "value": entities.quantity_value,
            "unit": entities.quantity_unit
        }
        if entities.quantity_value >= 1000:
            confidence = min(1.0, confidence + 0.1)
    
    return PatternMatch(
        pattern_type=ViolationPattern.COUNTERFEIT_SITE,
        confidence=confidence,
        evidence=evidence,
        keywords_matched=matched,
        details=details
    )


def analyze_violation_patterns(text: str) -> ViolationAnalysis:
    """Analyze article text for all violation patterns.
    
    This is the main entry point for violation pattern detection.
    It runs all pattern detectors and returns a comprehensive analysis.
    
    Args:
        text: Article text to analyze
        
    Returns:
        ViolationAnalysis with primary pattern, all matches, entities, and risk factors
    """
    if not text:
        return ViolationAnalysis(
            primary_pattern=ViolationPattern.UNKNOWN,
            primary_confidence=0.0
        )
    
    # Extract entities first for enhanced detection
    entities = extract_entities(text)
    
    # Run all pattern detectors
    patterns = [
        detect_door_to_door(text),
        detect_vehicle_transport(text, entities),
        detect_logistics_delivery(text),
        detect_maritime_smuggling(text),
        detect_counterfeit_site(text, entities),
    ]
    
    # Filter patterns with any confidence
    detected_patterns = [p for p in patterns if p.confidence > 0]
    
    # Determine primary pattern (highest confidence)
    if detected_patterns:
        primary = max(detected_patterns, key=lambda p: p.confidence)
        primary_pattern = primary.pattern_type
        primary_confidence = primary.confidence
    else:
        primary_pattern = ViolationPattern.UNKNOWN
        primary_confidence = 0.0
    
    # Extract additional risk factors
    risk_factors = _extract_risk_factors(text, entities)
    
    # Extract geographic hints
    geographic_hints = _extract_geographic_hints(text)
    
    # Extract temporal hints
    temporal_hints = _extract_temporal_hints(text)
    
    return ViolationAnalysis(
        primary_pattern=primary_pattern,
        primary_confidence=primary_confidence,
        all_patterns=detected_patterns,
        entities=entities,
        risk_factors=risk_factors,
        geographic_hints=geographic_hints,
        temporal_hints=temporal_hints
    )


def _extract_risk_factors(text: str, entities: Optional[CaseEntities]) -> List[str]:
    """Extract additional risk indicators from text."""
    factors = []
    
    # High-value risk factors
    high_value_patterns = [
        ("涉案金额大", ["涉案金额", "案值", "价值超过"]),
        ("跨省/跨境", ["跨省", "跨市", "跨境", "省际", "边境"]),
        ("有组织犯罪", ["团伙", "集团", "组织", "网络", "链条"]),
        ("惯犯/累犯", ["累犯", "惯犯", "前科", "多次", "再次"]),
        ("暴力抗法", ["暴力", "抗拒", "冲卡", "逃逸", "拒捕"]),
        ("公职人员涉入", ["公职人员", "干部", "公务员", "执法人员"]),
    ]
    
    for factor_name, keywords in high_value_patterns:
        if any(kw in text for kw in keywords):
            factors.append(factor_name)
    
    # Entity-based risk factors
    if entities:
        if entities.monetary_value and entities.monetary_value >= 500000:
            factors.append("涉案金额超50万")
        if entities.quantity_value and entities.quantity_value >= 1000:
            factors.append("查获数量超千条")
        if len(entities.suspects) >= 2:
            factors.append("多人涉案")
        if entities.vehicle_info:
            factors.append("涉及车辆")
    
    return factors


def _extract_geographic_hints(text: str) -> List[str]:
    """Extract geographic location hints from text."""
    hints = []
    
    # Province names
    provinces = [
        "北京", "天津", "上海", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江",
        "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
        "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "台湾",
        "内蒙古", "广西", "西藏", "宁夏", "新疆", "香港", "澳门"
    ]
    
    for province in provinces:
        if province in text:
            hints.append(province)
    
    # Major cities
    cities = [
        "广州", "深圳", "珠海", "汕头", "佛山", "东莞", "中山", "惠州",
        "福州", "厦门", "泉州", "漳州",
        "杭州", "宁波", "温州", "嘉兴",
        "南京", "苏州", "无锡", "常州",
        "武汉", "长沙", "南昌", "合肥",
        "成都", "重庆", "昆明", "贵阳",
        "郑州", "济南", "青岛", "烟台",
        "沈阳", "大连", "长春", "哈尔滨",
    ]
    
    for city in cities:
        if city in text and city not in hints:
            hints.append(city)
    
    return hints[:10]  # Limit to 10 hints


def _extract_temporal_hints(text: str) -> List[str]:
    """Extract temporal clues from text."""
    import re
    hints = []
    
    # Date patterns
    date_patterns = [
        (r"(\d{4}年\d{1,2}月\d{1,2}日)", "full_date"),
        (r"(\d{1,2}月\d{1,2}日)", "month_date"),
        (r"(\d{4}年\d{1,2}月)", "year_month"),
        (r"(凌晨|上午|下午|晚上|深夜)", "time_of_day"),
        (r"(周一|周二|周三|周四|周五|周六|周日|星期一|星期二|星期三|星期四|星期五|星期六|星期日)", "day_of_week"),
    ]
    
    for pattern, hint_type in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            hints.append(f"{hint_type}:{match}")
    
    return hints[:5]  # Limit to 5 hints


def get_pattern_display_name(pattern: ViolationPattern) -> str:
    """Get Chinese display name for a violation pattern."""
    names = {
        ViolationPattern.DOOR_TO_DOOR: "上门推销",
        ViolationPattern.VEHICLE_TRANSPORT: "专车运输",
        ViolationPattern.LOGISTICS_DELIVERY: "物流配送",
        ViolationPattern.MARITIME_SMUGGLING: "海上走私",
        ViolationPattern.COUNTERFEIT_SITE: "假烟制售点",
        ViolationPattern.UNKNOWN: "未知模式",
    }
    return names.get(pattern, pattern.value)