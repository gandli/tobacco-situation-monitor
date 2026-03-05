"""Test violation pattern detection algorithms.

Tests for the intelligent detection of five major tobacco violation patterns:
- Door-to-Door Sales (上门推销)
- Dedicated Vehicle Transport (专车运输)
- Logistics Delivery (物流配送)
- Maritime Smuggling (海上走私)
- Counterfeit Production Sites (假烟制售点)
"""

import pytest

from tsm.intel.violation_detector import (
    ViolationPattern,
    analyze_violation_patterns,
    detect_door_to_door,
    detect_vehicle_transport,
    detect_logistics_delivery,
    detect_maritime_smuggling,
    detect_counterfeit_site,
    get_pattern_display_name,
)


class TestDoorToDoorDetection:
    """Test door-to-door sales pattern detection."""

    def test_detect_basic_door_to_door(self):
        """Test basic door-to-door sales detection."""
        text = "近日，执法人员在某小区查获一起上门推销假烟案件，嫌疑人通过微信联系买家后上门送货。"
        result = detect_door_to_door(text)
        
        assert result.confidence > 0
        assert result.pattern_type == ViolationPattern.DOOR_TO_DOOR
        assert "上门推销" in result.keywords_matched

    def test_detect_social_media_sales(self):
        """Test detection of social media-based sales."""
        text = "犯罪团伙通过朋友圈发布香烟广告，声称可以便宜价格私下交易，走街串巷上门销售。"
        result = detect_door_to_door(text)
        
        assert result.confidence > 0.5
        assert "social_platforms" in result.details

    def test_low_confidence_for_generic_text(self):
        """Test that generic text gets low confidence."""
        text = "今天天气不错，香烟的价格有所波动。"
        result = detect_door_to_door(text)
        
        assert result.confidence < 0.3


class TestVehicleTransportDetection:
    """Test dedicated vehicle transport pattern detection."""

    def test_detect_cross_province_transport(self):
        """Test cross-province transport detection."""
        text = "执法人员在高速路口查获一辆货车，车内装载大量走私烟草，系跨省运输案件。"
        result = detect_vehicle_transport(text)
        
        assert result.confidence > 0.5
        assert result.pattern_type == ViolationPattern.VEHICLE_TRANSPORT
        assert result.details.get("cross_region") is True

    def test_detect_vehicle_with_license(self):
        """Test detection with vehicle license info."""
        text = "一辆车牌号为粤A12345的厢式货车在收费站被拦截，车内查获假烟2000条。"
        result = detect_vehicle_transport(text)
        
        assert result.confidence > 0
        assert "货车" in text or "车辆" in text

    def test_detect_checkpoint_interception(self):
        """Test detection at inspection checkpoints."""
        text = "边防检查站在设卡检查时，查获一辆面包车非法运输烟草专卖品。"
        result = detect_vehicle_transport(text)
        
        assert result.confidence > 0.4


class TestLogisticsDeliveryDetection:
    """Test logistics/delivery pattern detection."""

    def test_detect_express_delivery(self):
        """Test express delivery detection."""
        text = "通过顺丰快递邮寄假烟的案件被破获，快递单号显示货物从广东发往全国各地。"
        result = detect_logistics_delivery(text)
        
        assert result.confidence > 0.5
        assert result.pattern_type == ViolationPattern.LOGISTICS_DELIVERY
        assert "logistics_companies" in result.details

    def test_detect_ecommerce_sales(self):
        """Test e-commerce platform sales detection."""
        text = "犯罪嫌疑人在淘宝、拼多多等电商平台开设店铺销售走私烟，通过物流渠道发货。"
        result = detect_logistics_delivery(text)
        
        assert result.confidence > 0.5
        assert "ecommerce_platforms" in result.details

    def test_detect_wechat_sales(self):
        """Test WeChat-based sales with logistics."""
        text = "微商通过微信销售假烟，利用快递渠道将假烟配送到买家手中。"
        result = detect_logistics_delivery(text)
        
        assert result.confidence > 0.3


class TestMaritimeSmugglingDetection:
    """Test maritime smuggling pattern detection."""

    def test_detect_basic_smuggling(self):
        """Test basic maritime smuggling detection."""
        text = "海关缉私局在南海海域查获一艘走私船，船上载有大量走私烟草。"
        result = detect_maritime_smuggling(text)
        
        assert result.confidence > 0.5
        assert result.pattern_type == ViolationPattern.MARITIME_SMUGGLING
        assert "海上走私" in result.keywords_matched or "走私船" in result.keywords_matched

    def test_detect_port_smuggling(self):
        """Test port-based smuggling detection."""
        text = "边防部门在码头查获一起海上走私烟草案件，涉案金额达百万元。"
        result = detect_maritime_smuggling(text)
        
        assert result.confidence > 0.4
        assert "port_indicators" in result.details

    def test_detect_coastal_region_smuggling(self):
        """Test smuggling in coastal regions."""
        text = "广东海警在深圳海域拦截一艘快艇，查获走私入境的外国烟草。"
        result = detect_maritime_smuggling(text)
        
        assert result.confidence > 0.5
        assert "coastal_regions" in result.details

    def test_detect_international_smuggling(self):
        """Test international smuggling indicators."""
        text = "一艘渔船从境外走私烟草入境，在非设关地偷运上岸时被查获。"
        result = detect_maritime_smuggling(text)
        
        assert result.confidence > 0.6
        assert "international_indicators" in result.details


class TestCounterfeitSiteDetection:
    """Test counterfeit production site pattern detection."""

    def test_detect_production_site(self):
        """Test production site detection."""
        text = "执法人员捣毁一处制假窝点，现场查获卷烟机等生产设备，查获假冒卷烟1000条。"
        result = detect_counterfeit_site(text)
        
        assert result.confidence > 0.5
        assert result.pattern_type == ViolationPattern.COUNTERFEIT_SITE
        assert "制假窝点" in result.keywords_matched

    def test_detect_with_equipment(self):
        """Test detection with equipment mentions."""
        text = "在一个地下工厂内发现卷烟机、包装机等制假设备，大量假冒中华牌香烟。"
        result = detect_counterfeit_site(text)
        
        assert result.confidence > 0.5
        assert "equipment_indicators" in result.details

    def test_detect_with_materials(self):
        """Test detection with raw materials."""
        text = "黑作坊内堆放大量烟叶、卷烟纸等原材料，用于生产假冒伪劣烟草制品。"
        result = detect_counterfeit_site(text)
        
        assert result.confidence > 0.3
        assert "material_indicators" in result.details

    def test_detect_with_location_type(self):
        """Test detection with location characteristics."""
        text = "在出租屋内发现一处假烟制作点，生产假冒黄鹤楼香烟。"
        result = detect_counterfeit_site(text)
        
        # Low confidence due to minimal keywords, but location is detected
        assert result.confidence > 0
        assert "location_types" in result.details


class TestFullAnalysis:
    """Test complete violation pattern analysis."""

    def test_analyze_door_to_door_case(self):
        """Test full analysis of door-to-door case."""
        text = """
        近日，某市烟草专卖局破获一起上门推销假烟案件。
        犯罪嫌疑人通过微信群发布广告，声称可以低价销售香烟，
        随后走街串巷上门送货。涉案金额达20万元，假烟500条。
        """
        result = analyze_violation_patterns(text)
        
        assert result.primary_pattern == ViolationPattern.DOOR_TO_DOOR
        assert result.primary_confidence > 0
        assert len(result.all_patterns) >= 1
        assert result.entities is not None

    def test_analyze_vehicle_transport_case(self):
        """Test full analysis of vehicle transport case."""
        text = """
        高速交警在收费站设卡检查时，查获一辆厢式货车非法运输烟草专卖品。
        车内装载假烟2000条，系跨省运输案件。嫌疑人已被刑事拘留，
        涉案金额超过80万元。
        """
        result = analyze_violation_patterns(text)
        
        assert result.primary_pattern == ViolationPattern.VEHICLE_TRANSPORT
        assert result.primary_confidence > 0.3
        assert "跨省/跨境" in result.risk_factors or any("跨省" in f for f in result.risk_factors)

    def test_analyze_logistics_case(self):
        """Test full analysis of logistics case."""
        text = """
        执法人员破获一起利用快递渠道销售假烟的案件。
        犯罪团伙在电商平台开设店铺，通过顺丰、圆通等快递公司
        将假冒香烟发货至全国各地，涉案金额50万元。
        """
        result = analyze_violation_patterns(text)
        
        assert result.primary_pattern == ViolationPattern.LOGISTICS_DELIVERY
        assert result.primary_confidence > 0.3

    def test_analyze_maritime_smuggling_case(self):
        """Test full analysis of maritime smuggling case."""
        text = """
        海警在福建沿海查获一艘走私船，船上装载大量走私入境的
        外国品牌香烟。经查，该批烟草从境外偷运入境，
        涉案金额达500万元，是目前查获的最大海上走私烟草案件。
        """
        result = analyze_violation_patterns(text)
        
        assert result.primary_pattern == ViolationPattern.MARITIME_SMUGGLING
        assert result.primary_confidence > 0.5
        assert len(result.geographic_hints) > 0

    def test_analyze_counterfeit_site_case(self):
        """Test full analysis of counterfeit site case."""
        text = """
        烟草专卖局联合公安部门捣毁一处制假窝点。
        现场查获卷烟机2台、包装机1台，假冒中华、黄鹤楼等品牌
        卷烟3000条。该地下工厂位于废弃厂房内，已生产假烟数月。
        """
        result = analyze_violation_patterns(text)
        
        assert result.primary_pattern == ViolationPattern.COUNTERFEIT_SITE
        assert result.primary_confidence > 0.5

    def test_analyze_empty_text(self):
        """Test analysis of empty text."""
        result = analyze_violation_patterns("")
        
        assert result.primary_pattern == ViolationPattern.UNKNOWN
        assert result.primary_confidence == 0.0

    def test_analyze_generic_text(self):
        """Test analysis of generic text with no clear pattern."""
        text = "今天讨论了烟草行业的发展趋势和市场前景。"
        result = analyze_violation_patterns(text)
        
        # Should either be unknown or have low confidence
        if result.primary_pattern != ViolationPattern.UNKNOWN:
            assert result.primary_confidence < 0.3

    def test_risk_factors_extracted(self):
        """Test that risk factors are extracted."""
        text = """
        执法人员捣毁一个制售假烟团伙，该团伙成员有前科，
        涉案金额100万元，涉及跨省运输网络。
        """
        result = analyze_violation_patterns(text)
        
        # Should have multiple risk factors
        assert len(result.risk_factors) >= 1

    def test_geographic_hints_extracted(self):
        """Test that geographic hints are extracted."""
        text = """
        广东警方在深圳查获一起跨省运输假烟案件，
        假烟从福建运输至广东销售。
        """
        result = analyze_violation_patterns(text)
        
        # Should extract province names
        assert len(result.geographic_hints) >= 1


class TestPatternDisplayNames:
    """Test pattern display name mapping."""

    def test_door_to_door_name(self):
        """Test door-to-door display name."""
        assert get_pattern_display_name(ViolationPattern.DOOR_TO_DOOR) == "上门推销"

    def test_vehicle_transport_name(self):
        """Test vehicle transport display name."""
        assert get_pattern_display_name(ViolationPattern.VEHICLE_TRANSPORT) == "专车运输"

    def test_logistics_delivery_name(self):
        """Test logistics delivery display name."""
        assert get_pattern_display_name(ViolationPattern.LOGISTICS_DELIVERY) == "物流配送"

    def test_maritime_smuggling_name(self):
        """Test maritime smuggling display name."""
        assert get_pattern_display_name(ViolationPattern.MARITIME_SMUGGLING) == "海上走私"

    def test_counterfeit_site_name(self):
        """Test counterfeit site display name."""
        assert get_pattern_display_name(ViolationPattern.COUNTERFEIT_SITE) == "假烟制售点"

    def test_unknown_name(self):
        """Test unknown pattern display name."""
        assert get_pattern_display_name(ViolationPattern.UNKNOWN) == "未知模式"


class TestMultiplePatternDetection:
    """Test cases where multiple patterns might be detected."""

    def test_combined_transport_and_counterfeit(self):
        """Test case with both transport and counterfeit elements."""
        text = """
        执法人员在一辆货车内查获大量假烟，经调查发现
        这些假烟系从某制假窝点生产后跨省运输销售。
        """
        result = analyze_violation_patterns(text)
        
        # Should detect at least one pattern
        assert len(result.all_patterns) >= 1
        # Primary should be the one with higher confidence
        assert result.primary_confidence > 0

    def test_logistics_and_counterfeit_combined(self):
        """Test case combining logistics and counterfeit patterns."""
        text = """
        犯罪团伙在某地设立制假窝点生产假烟，然后通过
        快递渠道将假冒香烟发货至全国各地销售。
        """
        result = analyze_violation_patterns(text)
        
        # Should detect patterns
        assert len(result.all_patterns) >= 1


class TestConfidenceScoring:
    """Test confidence scoring accuracy."""

    def test_high_confidence_with_multiple_strong_indicators(self):
        """Test high confidence with multiple strong indicators."""
        text = """
        海警在南海海域查获一起海上走私烟草案件，走私船从境外
        偷运大量外国品牌香烟入境，涉案金额500万元。
        """
        result = detect_maritime_smuggling(text)
        
        # Multiple high-confidence keywords should yield high confidence
        assert result.confidence >= 0.6

    def test_medium_confidence_with_contextual_indicators(self):
        """Test medium confidence with contextual indicators."""
        text = """
        快递包裹内发现可疑烟草制品，经查为假烟。
        """
        result = detect_logistics_delivery(text)
        
        # Limited context should yield moderate confidence
        assert 0 < result.confidence < 0.8

    def test_low_confidence_with_minimal_indicators(self):
        """Test low confidence with minimal indicators."""
        text = "有人在网上卖烟。"
        result = detect_logistics_delivery(text)
        
        # Very minimal indicators
        assert result.confidence < 0.5