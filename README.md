# Olist E-Commerce Analytics Project

An end-to-end analytics project built with Python, Pandas, SQL-ready data layers,
Jupyter, Excel, and Power BI-oriented outputs using the public Brazilian Olist
e-commerce dataset.

## Project capabilities

- Ingest and validate CSV and Excel source files
- Profile and clean the nine Olist source datasets
- Generate revenue and product-category analysis
- Build RFM customer segmentation outputs
- Serve an interactive Streamlit dashboard
- Preserve raw source data separately from processed outputs

## Suggested environment

Use a dedicated project virtual environment and install dependencies through:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Repository structure

- `data/` stores raw, processed, external, and reference datasets
- `notebooks/` contains analysis and exploration notebooks
- `src/` contains Python modules for ETL and analysis
- `sql/` stores schema, staging, and model scripts
- `output/` stores generated Excel, charts, reports, and exports
- `tests/` stores validation and quality checks
- `logs/` stores runtime and execution logs
- `config/` stores configuration and environment settings

## Run the dashboard

Use the project virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run src/dashboard.py
```

The dashboard uses processed files in `data/processed` and is available at
`http://localhost:8501` after startup.

## Run the project workflows

```powershell
python src/data_profiling.py
python src/data_cleaning.py
python src/exploratory_analysis.py
python src/customer_segmentation.py
```

## Repository structure

- `data/raw/` stores original source files and is excluded from Git
- `data/processed/` stores generated cleaned and analytical files
- `src/` contains ingestion, profiling, cleaning, analysis, segmentation, and dashboard code
- `reports/` stores summaries and generated figures
- `sql/` stores schema, staging, validation, and mart SQL areas
- `tests/` stores automated validation tests
- `config/` stores project configuration
- `logs/` stores runtime logs

## Data safety

Raw data is never edited by the project workflows. Generated data, reports,
credentials, virtual environments, caches, and IDE settings are excluded through
`.gitignore`.
