"""Test entity extraction module."""

import pytest

from tsm.intel.entity_extractor import (
    extract_entities,
    extract_monetary_amount,
    extract_quantity,
    extract_suspects,
    extract_brands,
    extract_vehicle,
    extract_case_number,
    CaseEntities,
)


def test_extract_monetary_amount_yuan():
    """Test extracting monetary amount in yuan."""
    text = "涉案金额50万元，目前案件正在进一步调查中"
    raw, value = extract_monetary_amount(text)
    
    assert raw is not None
    assert value == 500000.0


def test_extract_monetary_amount_large():
    """Test extracting large monetary amount."""
    text = "本案案值高达1.2亿元"
    raw, value = extract_monetary_amount(text)
    
    assert value == 120000000.0


def test_extract_monetary_amount_not_found():
    """Test when no monetary amount is found."""
    text = "案件详情请见后续报道"
    raw, value = extract_monetary_amount(text)
    
    assert raw is None
    assert value is None


def test_extract_quantity_cartons():
    """Test extracting quantity in cartons."""
    text = "查获假冒卷烟1000条"
    raw, value, unit = extract_quantity(text)
    
    assert raw is not None
    assert value == 1000.0
    assert unit == "条"


def test_extract_quantity_cases():
    """Test extracting quantity in cases."""
    text = "共计查获卷烟500件"
    raw, value, unit = extract_quantity(text)
    
    assert unit == "件"


def test_extract_quantity_not_found():
    """Test when no quantity is found."""
    text = "案件已移交检察院"
    raw, value, unit = extract_quantity(text)
    
    assert raw is None
    assert value is None
    assert unit is None


def test_extract_suspects():
    """Test extracting suspect names."""
    text = "犯罪嫌疑人张某已被刑事拘留，同案犯李某在逃"
    suspects = extract_suspects(text)
    
    assert len(suspects) >= 1
    assert "张某" in suspects


def test_extract_suspects_multiple():
    """Test extracting multiple suspects."""
    text = "嫌疑人王某、赵某因涉嫌非法经营罪被逮捕"
    suspects = extract_suspects(text)
    
    assert len(suspects) >= 1


def test_extract_brands():
    """Test extracting tobacco brands."""
    text = "查获假冒中华、黄鹤楼卷烟共计200条"
    brands = extract_brands(text)
    
    assert "中华" in brands
    assert "黄鹤楼" in brands


def test_extract_brands_foreign():
    """Test extracting foreign tobacco brands."""
    text = "走私万宝路、555香烟案值巨大"
    brands = extract_brands(text)
    
    assert "万宝路" in brands
    assert "555" in brands


def test_extract_vehicle_license_plate():
    """Test extracting vehicle license plate."""
    text = "涉案车辆为粤B12345货车"
    vehicle = extract_vehicle(text)
    
    assert vehicle is not None
    assert "粤B12345" in vehicle


def test_extract_case_number():
    """Test extracting case number."""
    text = "本案案号为2026刑初字第123号"
    case_num = extract_case_number(text)
    
    assert case_num is not None
    assert "2026" in case_num


def test_extract_entities_comprehensive():
    """Test comprehensive entity extraction."""
    text = """
    近日，广东省深圳市市场监管局查获一起假冒卷烟案件。
    涉案金额高达80万元，查获假冒中华、芙蓉王卷烟共计2000条。
    犯罪嫌疑人李某已被刑事拘留，涉案车辆粤B88888已扣押。
    案件编号：2026刑初字第456号。
    """
    entities = extract_entities(text)
    
    assert entities.monetary_value == 800000.0
    assert entities.quantity_value == 2000.0
    assert entities.quantity_unit == "条"
    assert "中华" in entities.brands
    assert "芙蓉王" in entities.brands
    assert entities.vehicle_info is not None
    assert entities.case_number is not None
    assert entities.confidence >= 0.5


def test_extract_entities_empty():
    """Test with empty text."""
    entities = extract_entities("")
    
    assert entities.monetary_amount is None
    assert entities.monetary_value is None
    assert entities.quantity is None
    assert entities.suspects == []
    assert entities.brands == []
    assert entities.confidence == 0.0


def test_case_entities_dataclass():
    """Test CaseEntities dataclass defaults."""
    entities = CaseEntities()
    
    assert entities.suspects == []
    assert entities.brands == []
    assert entities.confidence == 0.0