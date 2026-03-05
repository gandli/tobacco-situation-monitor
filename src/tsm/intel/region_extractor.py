"""Region extraction and identification module.

This module extracts province/city/district information from article text
using pattern matching against a comprehensive region database.
"""

import re
from dataclasses import dataclass
from typing import Optional

# China provinces, autonomous regions, and municipalities
PROVINCES = [
    "北京市", "天津市", "上海市", "重庆市",
    "河北省", "山西省", "辽宁省", "吉林省", "黑龙江省",
    "江苏省", "浙江省", "安徽省", "福建省", "江西省", "山东省",
    "河南省", "湖北省", "湖南省", "广东省", "海南省",
    "四川省", "贵州省", "云南省", "陕西省", "甘肃省", "青海省",
    "台湾省",
    "内蒙古自治区", "广西壮族自治区", "西藏自治区",
    "宁夏回族自治区", "新疆维吾尔自治区",
    "香港特别行政区", "澳门特别行政区",
]

# Province abbreviations for text matching
PROVINCE_ABBREVS = {
    "北京": "北京市", "天津": "天津市", "上海": "上海市", "重庆": "重庆市",
    "河北": "河北省", "山西": "山西省", "辽宁": "辽宁省", "吉林": "吉林省",
    "黑龙江": "黑龙江省", "江苏": "江苏省", "浙江": "浙江省", "安徽": "安徽省",
    "福建": "福建省", "江西": "江西省", "山东": "山东省", "河南": "河南省",
    "湖北": "湖北省", "湖南": "湖南省", "广东": "广东省", "海南": "海南省",
    "四川": "四川省", "贵州": "贵州省", "云南": "云南省", "陕西": "陕西省",
    "甘肃": "甘肃省", "青海": "青海省", "台湾": "台湾省",
    "内蒙古": "内蒙古自治区", "广西": "广西壮族自治区", "西藏": "西藏自治区",
    "宁夏": "宁夏回族自治区", "新疆": "新疆维吾尔自治区",
    "香港": "香港特别行政区", "澳门": "澳门特别行政区",
}

# Major cities (prefecture-level and above)
MAJOR_CITIES = [
    # 省会城市
    "石家庄市", "太原市", "沈阳市", "长春市", "哈尔滨市",
    "南京市", "杭州市", "合肥市", "福州市", "南昌市", "济南市",
    "郑州市", "武汉市", "长沙市", "广州市", "海口市", "成都市",
    "贵阳市", "昆明市", "西安市", "兰州市", "西宁市",
    "呼和浩特市", "南宁市", "拉萨市", "银川市", "乌鲁木齐市",
    # 重要地级市
    "深圳市", "珠海市", "东莞市", "佛山市", "惠州市", "中山市",
    "苏州市", "无锡市", "宁波市", "温州市", "厦门市", "青岛市",
    "大连市", "唐山市", "大庆市", "徐州市", "洛阳市",
]

# Districts that might be mistaken for cities (especially in direct-controlled municipalities)
DISTRICTS = [
    "朝阳区", "海淀区", "浦东新区", "南山区", "福田区",
    "西城区", "东城区", "丰台区", "石景山区", "门头沟区",
    "房山区", "通州区", "顺义区", "昌平区", "大兴区",
    "怀柔区", "平谷区", "密云区", "延庆区",
]

# Common region patterns in news text
REGION_PATTERNS = [
    # Full province name
    r"([\u4e00-\u9fa5]{2,6}(?:省|自治区|直辖市|特别行政区))",
    # Province abbreviation + city
    r"([\u4e00-\u9fa5]{2,4})(?:省|市)?([\u4e00-\u9fa5]{2,6}市)",
    # County/district level
    r"([\u4e00-\u9fa5]{2,6}(?:县|区|旗))",
    # Place markers
    r"在(.*?(?:省|市|县|区))",
    r"位于(.*?(?:省|市|县|区))",
    r"(.*?(?:省|市|县|区))(?:抓获|查获|破获)",
]


@dataclass
class RegionInfo:
    """Extracted region information."""
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    raw_text: Optional[str] = None
    confidence: float = 0.0


def extract_region(text: str) -> RegionInfo:
    """Extract region information from article text.

    Uses pattern matching to identify province, city, and district
    mentions in Chinese news articles.

    Args:
        text: Article text to analyze.

    Returns:
        RegionInfo with extracted province, city, district, and confidence.
    """
    if not text:
        return RegionInfo()

    province = None
    city = None
    district = None
    raw_text = None

    # Try to find province first (full name or abbreviation)
    for abbrev, full_name in PROVINCE_ABBREVS.items():
        if abbrev in text:
            province = full_name
            break

    # If no abbreviation found, try full names
    if not province:
        for full_name in PROVINCES:
            if full_name in text:
                province = full_name
                break

    # Try to find district first (higher priority than city)
    # Check explicit districts list first
    for district_name in DISTRICTS:
        if district_name in text:
            district = district_name
            break
    
    # If no explicit district found, try pattern matching
    if not district:
        # Look for district/county patterns
        # Use a pattern that explicitly excludes 市 from the match
        # Match: any char except 市，followed by 1-2 chars, then 县区旗
        pattern = r'([^\u4e00-\u9fa5市州]?[\u4e00-\u9fa5]{1,2}[县区旗])'
        matches = re.findall(pattern, text)
        
        for candidate in matches:
            # Clean up and validate
            if not candidate:
                continue
            # Skip if contains 市
            if '市' in candidate:
                continue
            # Must be 2-4 chars total
            if 2 <= len(candidate) <= 4:
                district = candidate
                break

    # Try to find city - check MAJOR_CITIES first
    # But skip if it looks like a district (ends with 区 and is in DISTRICTS)
    for city_name in MAJOR_CITIES:
        if city_name in text:
            # Make sure this isn't actually a district
            if not (city_name.endswith('区') and city_name in DISTRICTS):
                city = city_name
                break

    # If no major city found, look for generic city patterns
    # But avoid matching patterns that are part of district names
    if not city:
        # Look for city pattern but exclude cases where it's followed by district indicators
        city_match = re.search(r"([\u4e00-\u9fa5]{2,4}市)(?![\u4e00-\u9fa5]*[县区旗])", text)
        if city_match:
            city = city_match.group(1)

    # Calculate confidence based on granularity
    confidence = 0.0
    if province:
        confidence = 0.4
        raw_text = province
    if city:
        confidence = 0.7
        raw_text = city if not raw_text else f"{raw_text} {city}"
    if district:
        confidence = 1.0
        raw_text = district if not raw_text else f"{raw_text} {district}"

    return RegionInfo(
        province=province,
        city=city,
        district=district,
        raw_text=raw_text,
        confidence=confidence
    )


def get_region_display(region: RegionInfo) -> str:
    """Get a display-friendly region string.

    Args:
        region: RegionInfo to format.

    Returns:
        Human-readable region string like "广东省 深圳市" or "北京市".
    """
    parts = []
    if region.province:
        parts.append(region.province)
    if region.city and region.city != region.province:
        parts.append(region.city)
    if region.district:
        parts.append(region.district)
    return " ".join(parts) if parts else "未知地区"