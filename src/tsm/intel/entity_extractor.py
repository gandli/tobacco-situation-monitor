"""Entity extraction module for tobacco case intelligence.

This module extracts key entities from article text including:
- 涉案金额 (monetary amounts involved)
- 涉案数量 (quantity of tobacco products)
- 嫌疑人 (suspects)
- 涉案品牌 (tobacco brands involved)
- 车辆信息 (vehicle information)
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CaseEntities:
    """Extracted entities from a case article."""
    monetary_amount: Optional[str] = None  # e.g., "50万元"
    monetary_value: Optional[float] = None  # e.g., 500000.0
    quantity: Optional[str] = None  # e.g., "1000条"
    quantity_value: Optional[float] = None  # e.g., 1000.0
    quantity_unit: Optional[str] = None  # e.g., "条", "件", "箱"
    suspects: List[str] = field(default_factory=list)
    brands: List[str] = field(default_factory=list)
    vehicle_info: Optional[str] = None
    case_number: Optional[str] = None  # e.g., "2026刑初字第123号"
    confidence: float = 0.0


# Monetary amount patterns
MONEY_PATTERNS = [
    r"涉案金额(.*?)(\d+(?:\.\d+)?)\s*(万元|元|万|亿元)",
    r"案值(.*?)(\d+(?:\.\d+)?)\s*(万元|元|万|亿元)",
    r"价值(.*?)(\d+(?:\.\d+)?)\s*(万元|元|万|亿元)",
    r"(\d+(?:\.\d+)?)\s*(万元|元|万|亿元)(.*?)案值",
    r"查获(.*?)(\d+(?:\.\d+)?)\s*(万元|元|万|亿元)(.*?)(?:假烟|烟草|卷烟)",
    r"(\d+(?:\.\d+)?)\s*万余元",
    r"(\d+(?:\.\d+)?)\s*万元",
]

# Quantity patterns
QUANTITY_PATTERNS = [
    r"(\d+(?:\.\d+)?)\s*(条|件|箱|盒|包|万支|支)",
    r"查获(.*?)(\d+(?:\.\d+)?)\s*(条|件|箱|盒|包|万支|支)",
    r"共计(.*?)(\d+(?:\.\d+)?)\s*(条|件|箱|盒|包|万支|支)",
]

# Suspect name patterns (Chinese names typically 2-4 characters)
# Use negative lookahead to avoid capturing extra characters after the name
SUSPECT_PATTERNS = [
    # Pattern for names like 张某 (surname + 某)
    r"嫌疑人?([A-Z][a-z])(?=[，,。.\s、]|已被|在逃|因|涉嫌|$)",
    r"犯罪嫌疑人?([A-Z][a-z])(?=[，,。.\s、]|已被|在逃|因|涉嫌|$)",
    r"被告人?([A-Z][a-z])(?=[，,。.\s、]|已被|在逃|因|涉嫌|$)",
    # Pattern for regular Chinese names (2-4 characters)
    r"嫌疑人?([\u4e00-\u9fa5]{2,4})(?=[，,。.\s、]|已被|在逃|因|涉嫌|$)",
    r"犯罪嫌疑人?([\u4e00-\u9fa5]{2,4})(?=[，,。.\s、]|已被|在逃|因|涉嫌|$)",
    r"被告人?([\u4e00-\u9fa5]{2,4})(?=[，,。.\s、]|已被|在逃|因|涉嫌|$)",
]

# Tobacco brand patterns
TOBACCO_BRANDS = [
    "中华", "黄鹤楼", "芙蓉王", "利群", "玉溪", "云烟", "南京", "红塔山",
    "双喜", "黄山", "贵烟", "黄金叶", "苏烟", "泰山", "七匹狼", "长白山",
    "红河", "白沙", "娇子", "兰州", "中南海", "红双喜", "熊猫",
    "万宝路", "555", "七星", "大卫杜夫", "骆驼", "健牌",
]

# Vehicle patterns
VEHICLE_PATTERNS = [
    r"([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼][A-Z][A-Z0-9]{5,6})",
    r"车牌号[:：]?\s*([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼][A-Z][A-Z0-9]{5,6})",
    r"驾驶(.*?车)",
    r"使用(.*?货车)",
    r"无牌(.*?车)",
]

# Case number patterns
CASE_NUMBER_PATTERNS = [
    r"(\d{4})[刑行]初字第(\d+)号",
    r"(\d{4})[刑行]终字第(\d+)号",
    r"案号[:：]?\s*(\d{4}[刑行].*?\d+号)",
]


def extract_monetary_amount(text: str) -> tuple[Optional[str], Optional[float]]:
    """Extract monetary amount from text.

    Args:
        text: Article text to search.

    Returns:
        Tuple of (raw_amount_string, numeric_value_in_yuan).
    """
    for pattern in MONEY_PATTERNS:
        match = re.search(pattern, text)
        if match:
            raw = match.group(0)
            # Extract numeric value
            nums = re.findall(r"(\d+(?:\.\d+)?)", raw)
            if nums:
                value = float(nums[0])
                # Check unit
                if "亿" in raw:
                    value *= 100000000
                elif "万" in raw:
                    value *= 10000
                return raw, value
    return None, None


def extract_quantity(text: str) -> tuple[Optional[str], Optional[float], Optional[str]]:
    """Extract tobacco quantity from text.

    Args:
        text: Article text to search.

    Returns:
        Tuple of (raw_quantity_string, numeric_value, unit).
    """
    for pattern in QUANTITY_PATTERNS:
        match = re.search(pattern, text)
        if match:
            raw = match.group(0)
            # Extract number and unit
            num_match = re.search(r"(\d+(?:\.\d+)?)", raw)
            unit_match = re.search(r"(条|件|箱|盒|包|万支|支)", raw)
            if num_match and unit_match:
                value = float(num_match.group(1))
                unit = unit_match.group(1)
                return raw, value, unit
    return None, None, None


def extract_suspects(text: str) -> List[str]:
    """Extract suspect names from text.

    Args:
        text: Article text to search.

    Returns:
        List of suspect names found.
    """
    suspects = []
    for pattern in SUSPECT_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                # Get the first non-empty group from the tuple
                match = next((g for g in match if g), match[-1])
            
            # Clean up the match - remove trailing punctuation or extra characters
            match = match.strip()
            
            # Filter out common false positives and ensure valid name length
            false_positives = ["查获", "破获", "抓获", "涉案", "执法", "已被", "在逃"]
            if match and len(match) >= 2 and len(match) <= 4 and match not in false_positives:
                # Remove any trailing punctuation that might have been captured
                match = re.sub(r'[，。、；：！？\s]+$', '', match)
                if match and match not in suspects:
                    suspects.append(match)
    return suspects[:5]  # Limit to top 5


def extract_brands(text: str) -> List[str]:
    """Extract tobacco brand names from text.

    Args:
        text: Article text to search.

    Returns:
        List of brand names found.
    """
    found = []
    for brand in TOBACCO_BRANDS:
        if brand in text:
            found.append(brand)
    return found


def extract_vehicle(text: str) -> Optional[str]:
    """Extract vehicle information from text.

    Args:
        text: Article text to search.

    Returns:
        Vehicle information string or None.
    """
    for pattern in VEHICLE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_case_number(text: str) -> Optional[str]:
    """Extract case number from text.

    Args:
        text: Article text to search.

    Returns:
        Case number string or None.
    """
    for pattern in CASE_NUMBER_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_entities(text: str) -> CaseEntities:
    """Extract all entities from article text.

    Args:
        text: Article text to analyze.

    Returns:
        CaseEntities with all extracted information.
    """
    if not text:
        return CaseEntities()

    # Extract monetary amount
    monetary_raw, monetary_val = extract_monetary_amount(text)

    # Extract quantity
    qty_raw, qty_val, qty_unit = extract_quantity(text)

    # Extract other entities
    suspects = extract_suspects(text)
    brands = extract_brands(text)
    vehicle = extract_vehicle(text)
    case_num = extract_case_number(text)

    # Calculate confidence
    confidence = 0.0
    if monetary_val:
        confidence += 0.3
    if qty_val:
        confidence += 0.2
    if suspects:
        confidence += 0.2
    if brands:
        confidence += 0.1
    if vehicle:
        confidence += 0.1
    if case_num:
        confidence += 0.1
    confidence = min(1.0, confidence)

    return CaseEntities(
        monetary_amount=monetary_raw,
        monetary_value=monetary_val,
        quantity=qty_raw,
        quantity_value=qty_val,
        quantity_unit=qty_unit,
        suspects=suspects,
        brands=brands,
        vehicle_info=vehicle,
        case_number=case_num,
        confidence=confidence
    )