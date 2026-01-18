from services.csv_analysis_service import CSVAnalysisService


def test_analyze_galamsay_basic():
    csv_content = """city,region,sites
A,R1,5
B,R1,7
C,R2,1
C,R2,3
"""
    res = CSVAnalysisService.analyze_galamsay(csv_content, threshold=5)
    assert res["total_sites"] == 16
    assert res["region_with_highest_sites"]["region"] == "R1"
    assert res["region_with_highest_sites"]["sites"] == 12
    # Only B exceeds threshold strictly (>5)
    cities = res["cities_exceeding_threshold"]
    assert any(c["city"] == "B" and c["sites"] == 7 for c in cities)
    assert not any(c["city"] == "A" for c in cities)
    # Averages per region
    avgs = res["average_sites_per_region"]
    assert abs(avgs["R1"] - 6.0) < 1e-9
    assert abs(avgs["R2"] - 4.0) < 1e-9


def test_analyze_galamsay_malformed_and_negative_values():
    csv_content = """city,region,sites
A,R1,5
B,R1,not_a_number
C,R2,-3
"""
    res = CSVAnalysisService.analyze_galamsay(csv_content, threshold=1)
    # B becomes 0, C negative clamped to 0 -> total = 5
    assert res["total_sites"] == 5


def test_analyze_content_summary_exists():
    csv_content = """col1,col2
1,2
3,4
"""
    res = CSVAnalysisService.analyze_content(csv_content)
    assert "columns" in res and res["columns"] == ["col1", "col2"]
    assert res["row_count"] == 2
    assert "summary" in res
