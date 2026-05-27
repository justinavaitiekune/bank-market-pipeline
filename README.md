# bank-market-data-pipeline

A PySpark and Delta Lake data pipeline running on Databricks that processes multi-bank market data using the Medallion Architecture (Bronze -> Silver -> Gold). 

The primary challenge of this project was handling a non-standard "wide-format" raw CSV where different bank entities were spread across indexed columns, requiring custom unpivoting logic to format it into a relational schema.

## Architecture & Data Flow

1. **Environment Setup (`00_setup_environment`)**: Runs a SQL DDL script to initialize the target Delta Lake schema (`main.market_project`) if it does not exist.
2. **Bronze (`01_bronze_ingestion`)**: Ingests raw multi-bank daily price CSV files directly into Delta format to preserve raw history and data lineage.
3. **Silver (`02_silver_transformation`)**: Extracts and isolates individual bank metrics (Danske Bank, Swedbank, EURUSD) using a parameterized helper function. Converts data types (`timestamp`, `double`, `long`), filters out secondary text headers via regex (`rlike`), and unpivots the data into a standardized "long-format" relational schema using `union`.
4. **Gold (`03_gold_transformation`)**: Computes time-series business metrics using Spark Window functions (`Window.partitionBy`). Calculated fields include `daily_return_pct` (via `lag`) and `moving_avg_7d`.

## Data Quality Suite (`04_data_quality_tests`)

To ensure pipeline reliability, a centralized testing notebook runs automated quality checks across all layers:
* **Schema Validation**: Explicitly verifies column structure and names in the Silver layer before analytical processing.
* **Null Audits**: Scans business-critical columns for missing values.
* **Lineage & Data Loss Analysis**: Performs a `left_anti` join between Bronze and Silver data to track exact row counts, calculate data loss percentages, and automatically isolate dropped records for debugging.

## Tech Stack
* Apache Spark (PySpark)
* Delta Lake
* Databricks
* Python 3.x

## Setup & Structure
* `data_ingestion.py`: Local environment setup script.
* `00_setup_environment.py`: Databricks initialization and path configurations.
* `01_bronze_ingestion.py`: Raw data landing notebook.
* `02_silver_transformation.py`: Cleaning, casting, and entity unpivoting logic.
* `03_gold_transformation.py`: Window functions and financial metrics calculation.
* `04_data_quality_tests.py`: End-to-end data validation and lineage reporting.