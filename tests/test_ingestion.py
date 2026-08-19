from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.etl.ingestion import load_csv, load_excel, validate_file_input


def test_validate_file_input_accepts_csv(tmp_path: Path) -> None:
    file_path = tmp_path / "data.csv"
    file_path.write_text("customer_id,amount\n1,100\n2,250\n", encoding="utf-8")

    validation = validate_file_input(file_path)

    assert validation["exists"] is True
    assert validation["file_type"] == "csv"
    assert validation["status"] == "ready"


def test_load_csv_reads_dataframe_and_validates_columns(tmp_path: Path) -> None:
    file_path = tmp_path / "orders.csv"
    pd.DataFrame(
        {
            "order_id": [101, 102],
            "sales_amount": [150.0, 225.5],
            "region": ["North", "South"],
        }
    ).to_csv(file_path, index=False)

    df = load_csv(file_path, expected_columns=["order_id", "sales_amount", "region"])

    assert list(df.columns) == ["order_id", "sales_amount", "region"]
    assert len(df) == 2


def test_load_excel_reads_dataframe(tmp_path: Path) -> None:
    file_path = tmp_path / "sales.xlsx"
    pd.DataFrame({"month": ["Jan", "Feb"], "revenue": [1200, 1400]}).to_excel(file_path, index=False)

    df = load_excel(file_path, expected_columns=["month", "revenue"])

    assert list(df.columns) == ["month", "revenue"]
    assert df["revenue"].sum() == 2600
