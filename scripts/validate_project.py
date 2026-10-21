#!/usr/bin/env python3
"""Validate generated financial data and dashboard structure before Pages deployment."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def main():
    data=json.loads((ROOT/"data/financial_data.json").read_text(encoding="utf-8"))
    public=json.loads((ROOT/"docs/data.json").read_text(encoding="utf-8"))
    assert data==public,"docs/data.json must match data/financial_data.json"
    assert data.get("company",{}).get("stock_code")=="005930","Company configuration mismatch"
    for key in ("annual","half_year","quarterly","peers"):
        assert isinstance(data.get(key),list),f"{key} must be a list"
    assert len(data["peers"])>=3,"Peer firm table is missing reference firms"
    for category in ("annual","half_year","quarterly"):
        for row in data[category]:
            assert isinstance(row.get("year"),int),f"Missing year in {category}"
            assert row.get("period") is not None,f"Missing period in {category}"
    html=(ROOT/"docs/index.html").read_text(encoding="utf-8")
    for element_id in ("annualTable","halfYearTable","quarterlyTable","peerTable","yearFilter","performanceChart","balanceChart"):
        assert f'id="{element_id}"' in html,f"Dashboard is missing element {element_id}"
    assert "fetch('./data.json'" in html,"Dashboard must load the current published data JSON"
    print("Project validation PASS")
    print(f"annual={len(data['annual'])}, half_year={len(data['half_year'])}, quarterly={len(data['quarterly'])}, peer_firms={len(data['peers'])}")
if __name__=="__main__":main()
