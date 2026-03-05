"""Test region extraction module."""

import pytest

from tsm.intel.region_extractor import (
    extract_region,
    get_region_display,
    RegionInfo,
)


def test_extract_province_full_name():
    """Test extracting province with full name."""
    text = "近日，广东省深圳市执法部门查获一批假烟..."
    result = extract_region(text)
    
    assert result.province == "广东省"
    assert result.confidence >= 0.4


def test_extract_province_abbreviation():
    """Test extracting province from abbreviation."""
    text = "北京警方破获一起烟草走私案件"
    result = extract_region(text)
    
    assert result.province == "北京市"


def test_extract_city():
    """Test extracting city information."""
    text = "广州市烟草专卖局开展专项行动"
    result = extract_region(text)
    
    assert result.city == "广州市"
    assert result.confidence >= 0.7


def test_extract_district():
    """Test extracting district information."""
    text = "浦东新区市场监管局查处无证经营"
    result = extract_region(text)
    
    assert result.district == "浦东新区"
    assert result.confidence >= 0.7


def test_extract_multiple_levels():
    """Test extracting province, city, and district together."""
    text = "浙江省杭州市西湖区法院宣判一起烟草案件"
    result = extract_region(text)
    
    assert result.province == "浙江省"
    assert result.city == "杭州市"
    assert result.district == "西湖区"
    assert result.confidence == 1.0


def test_no_region_found():
    """Test when no region information is present."""
    text = "今日破获一起案件，详情请见后续报道"
    result = extract_region(text)
    
    assert result.province is None
    assert result.city is None
    assert result.district is None
    assert result.confidence == 0.0


def test_empty_text():
    """Test with empty text."""
    result = extract_region("")
    
    assert result.province is None
    assert result.confidence == 0.0


def test_get_region_display():
    """Test region display formatting."""
    region = RegionInfo(
        province="广东省",
        city="深圳市",
        district="南山区"
    )
    display = get_region_display(region)
    
    assert display == "广东省 深圳市 南山区"


def test_get_region_display_empty():
    """Test region display with no region."""
    region = RegionInfo()
    display = get_region_display(region)
    
    assert display == "未知地区"


def test_autonomous_region():
    """Test extracting autonomous region."""
    text = "内蒙古自治区呼和浩特市查获走私烟草"
    result = extract_region(text)
    
    assert result.province == "内蒙古自治区"


def test_municipality():
    """Test extracting municipality."""
    text = "上海市烟草专卖局发布公告"
    result = extract_region(text)
    
    assert result.province == "上海市"