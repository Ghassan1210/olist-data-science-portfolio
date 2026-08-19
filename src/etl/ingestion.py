"""Reusable data ingestion routines for raw CSV and Excel files."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd

logger = logging.getLogger(__name__)

SUPPORTED_FILE_TYPES = {"csv", "xlsx", "xls"}
DEFAULT_CSV_ENCODINGS = ("utf-8-sig", "utf-8", "cp1252", "latin-1")


def validate_file_input(file_path: str | Path, encoding: str = "utf-8-sig") -> dict:
    """Validate a raw file before ingesting it.

    Returns a dictionary with the file status and metadata used by downstream
    ingestion functions. The structure is intentionally simple and convenient for
    logging and QA checks.
    """
    path = Path(file_path)
    result: dict[str, object] = {
        "path": str(path),
        "exists": False,
        "is_file": False,
        "file_type": "unknown",
        "status": "missing",
        "size_bytes": 0,
    }

    if not path.exists():
        logger.warning("Input file does not exist: %s", path)
        return result

    result["exists"] = True
    result["is_file"] = path.is_file()

    if not path.is_file():
        result["status"] = "not_a_file"
        logger.error("Input path is not a file: %s", path)
        return result

    suffix = path.suffix.lower().lstrip(".")
    result["file_type"] = suffix if suffix else "unknown"
    result["size_bytes"] = path.stat().st_size

    if suffix not in SUPPORTED_FILE_TYPES:
        result["status"] = "unsupported"
        logger.error("Unsupported file type for %s: %s", path, suffix)
        return result

    if result["size_bytes"] == 0:
        result["status"] = "empty"
        logger.warning("Input file is empty: %s", path)
        return result

    try:
        if suffix == "csv":
            with path.open("r", encoding=encoding, newline="") as handle:
                preview = handle.read(2048)
            if not preview.strip():
                result["status"] = "empty"
                logger.warning("CSV file contains no data: %s", path)
                return result
        else:
            df = pd.read_excel(path)
            if df.empty:
                result["status"] = "empty"
                logger.warning("Excel file contains no rows: %s", path)
                return result
    except (UnicodeDecodeError, ValueError, pd.errors.EmptyDataError) as exc:
        result["status"] = "invalid"
        logger.error("Input file could not be validated: %s", exc)
        return result

    result["status"] = "ready"
    logger.info("Input file validated successfully: %s", path)
    return result


def _validate_dataframe_schema(
    frame: pd.DataFrame,
    expected_columns: Iterable[str] | None = None,
    expected_dtypes: Mapping[str, str] | None = None,
    allow_unexpected_columns: bool = False,
) -> None:
    """Validate columns and basic pandas data types without changing the frame."""
    cols = list(expected_columns or [])
    missing_columns = [column for column in cols if column not in frame.columns]
    if missing_columns:
        missing_list = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns: {missing_list}")

    if not allow_unexpected_columns and cols:
        unexpected_columns = [column for column in frame.columns if column not in cols]
        if unexpected_columns:
            unexpected_list = ", ".join(unexpected_columns)
            raise ValueError(f"Unexpected columns: {unexpected_list}")

    for column, expected_type in (expected_dtypes or {}).items():
        if column not in frame.columns:
            raise ValueError(f"Cannot validate data type for missing column: {column}")

        series = frame[column].dropna()
        if expected_type == "numeric" and not pd.api.types.is_numeric_dtype(series):
            raise TypeError(f"Column '{column}' must be numeric")
        if expected_type == "integer" and not pd.api.types.is_integer_dtype(series):
            raise TypeError(f"Column '{column}' must contain integers")
        if expected_type == "string" and not series.map(lambda value: isinstance(value, str)).all():
            raise TypeError(f"Column '{column}' must contain strings")
        if expected_type == "datetime" and not pd.api.types.is_datetime64_any_dtype(series):
            raise TypeError(f"Column '{column}' must contain datetimes")


def load_csv(
    file_path: str | Path,
    expected_columns: Iterable[str] | None = None,
    expected_dtypes: Mapping[str, str] | None = None,
    allow_unexpected_columns: bool = False,
    encoding: str | None = None,
    encoding_fallbacks: Iterable[str] | None = None,
    delimiter: str = ",",
) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame with validation."""
    path = Path(file_path)
    encodings = list(dict.fromkeys([encoding] if encoding else []))
    encodings.extend(
        candidate
        for candidate in (encoding_fallbacks or DEFAULT_CSV_ENCODINGS)
        if candidate not in encodings
    )

    dataframe: pd.DataFrame | None = None
    last_error: Exception | None = None
    for candidate_encoding in encodings:
        validation = validate_file_input(path, encoding=candidate_encoding)
        if validation["status"] in {"missing", "not_a_file", "unsupported", "empty"}:
            raise ValueError(f"CSV file is not ready for ingestion: {path} ({validation['status']})")
        if validation["status"] != "ready":
            continue

        try:
            dataframe = pd.read_csv(path, encoding=candidate_encoding, sep=delimiter)
            logger.info("Loaded CSV using encoding %s: %s", candidate_encoding, path)
            break
        except (UnicodeDecodeError, pd.errors.ParserError) as exc:
            last_error = exc
            logger.warning("CSV encoding %s failed for %s", candidate_encoding, path)

    if dataframe is None:
        logger.exception("CSV ingestion failed for %s", path) if last_error else logger.error(
            "CSV validation failed for %s", path
        )
        raise ValueError(f"Unable to read CSV file: {path}") from last_error

    if dataframe.empty:
        raise ValueError(f"CSV file contains no rows: {path}")

    _validate_dataframe_schema(dataframe, expected_columns, expected_dtypes, allow_unexpected_columns)
    logger.info("Loaded CSV dataset with %s rows and %s columns from %s", len(dataframe), len(dataframe.columns), path)
    return dataframe


def load_excel(
    file_path: str | Path,
    expected_columns: Iterable[str] | None = None,
    expected_dtypes: Mapping[str, str] | None = None,
    allow_unexpected_columns: bool = False,
    sheet_name: int | str = 0,
) -> pd.DataFrame:
    """Load an Excel workbook into a pandas DataFrame with validation."""
    path = Path(file_path)
    validation = validate_file_input(path)

    if validation["status"] != "ready":
        raise ValueError(f"Excel file is not ready for ingestion: {path} ({validation['status']})")

    try:
        dataframe = pd.read_excel(path, sheet_name=sheet_name)
    except Exception as exc:  # pragma: no cover - bounded by validation and tests
        logger.exception("Excel ingestion failed for %s", path)
        raise ValueError(f"Unable to read Excel file: {path}") from exc

    if dataframe.empty:
        raise ValueError(f"Excel file contains no rows: {path}")

    _validate_dataframe_schema(dataframe, expected_columns, expected_dtypes, allow_unexpected_columns)
    logger.info("Loaded Excel dataset with %s rows and %s columns from %s", len(dataframe), len(dataframe.columns), path)
    return dataframe
