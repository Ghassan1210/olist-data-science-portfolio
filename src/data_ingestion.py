"""Public ingestion API for raw business data sources.

The implementation lives in ``src.etl.ingestion``; this module provides a
stable, shorter import path for scripts and notebooks.
"""

from src.etl.ingestion import load_csv, load_excel, validate_file_input

__all__ = ["load_csv", "load_excel", "validate_file_input"]
