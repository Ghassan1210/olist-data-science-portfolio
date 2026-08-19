from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.data_ingestion import load_csv, validate_file_input


PROJECT_ROOT = Path(__file__).parents[1]


def test_ingestion_config_defines_raw_source_defaults() -> None:
    config_path = PROJECT_ROOT / "config" / "ingestion_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    assert config["raw_data_directory"] == "data/raw"
    assert "csv" in config["supported_file_types"]
    assert config["fail_on_empty_dataset"] is True


def test_load_csv_honors_non_default_encoding(tmp_path: Path) -> None:
    file_path = tmp_path / "customers.csv"
    file_path.write_text("customer_id,name\n1,Andre\n", encoding="utf-16")

    dataframe = load_csv(file_path, encoding="utf-16", expected_columns=["customer_id", "name"])

    assert dataframe.iloc[0]["name"] == "Andre"


def test_load_csv_falls_back_for_common_legacy_encoding(tmp_path: Path) -> None:
    file_path = tmp_path / "customers.csv"
    file_path.write_bytes("customer_id,name\n1,Andre\n".encode("cp1252"))

    dataframe = load_csv(file_path, expected_columns=["customer_id", "name"])

    assert dataframe.iloc[0]["name"] == "Andre"


def test_validate_file_input_reports_missing_file(tmp_path: Path) -> None:
    validation = validate_file_input(tmp_path / "missing.csv")

    assert validation["status"] == "missing"
    assert validation["exists"] is False


def test_load_csv_rejects_missing_required_columns(tmp_path: Path) -> None:
    file_path = tmp_path / "orders.csv"
    pd.DataFrame({"order_id": [1], "amount": [100]}).to_csv(file_path, index=False)

    with pytest.raises(ValueError, match="Missing required columns: region"):
        load_csv(file_path, expected_columns=["order_id", "amount", "region"])


def test_load_csv_rejects_unexpected_columns(tmp_path: Path) -> None:
    file_path = tmp_path / "orders.csv"
    pd.DataFrame({"order_id": [1], "amount": [100], "loaded_at": ["2026-08-19"]}).to_csv(
        file_path, index=False
    )

    with pytest.raises(ValueError, match="Unexpected columns: loaded_at"):
        load_csv(file_path, expected_columns=["order_id", "amount"])


def test_load_csv_validates_basic_data_types(tmp_path: Path) -> None:
    file_path = tmp_path / "orders.csv"
    pd.DataFrame({"order_id": ["bad-id"], "amount": [100]}).to_csv(file_path, index=False)

    with pytest.raises(TypeError, match="Column 'order_id' must contain integers"):
        load_csv(file_path, expected_columns=["order_id", "amount"], expected_dtypes={"order_id": "integer"})
