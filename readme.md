# bank-market-data-pipeline

A PySpark and Delta Lake data pipeline running on Databricks that processes multi-asset market data using the Medallion Architecture (Bronze -> Silver -> Gold). 

The primary challenge of this project was transforming raw, heterogeneous API JSON responses into a structured, relational schema suitable for time-series analytics, ensuring data integrity across the Medallion layers.

## Architecture & Data Flow

1. **Environment Setup (`00_setup_environment`)**: Runs a SQL DDL script to initialize the target Delta Lake schema (`main.market_project`) if it does not exist.
2. **Bronze (`01_bronze_ingestion`)**: Ingests raw multi-asset daily price CSV files (generated from Alpha Vantage with strict 3-second API throttling to respect rate limits) directly into Delta format to preserve raw history and data lineage.
3. **Silver (`02_silver_transformation`)**: Extracts and isolates individual entity metrics (JPM, BAC, C, EURUSD) using a parameterized helper function. Converts data types (`timestamp`, `double`, `long`), filters out secondary text headers via regex (`rlike`), and unpivots the data into a standardized "long-format" relational schema using `union`.
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
* Alpha Vantage API

## Setup & Structure
* `databricks.yml`: Configuration for Databricks Asset Bundles (DABs), defining job orchestration and task dependencies.
* `data_ingestion.py`: A Python module containing utility functions for Alpha Vantage API interaction.
* `.env`: Local configuration file for API keys.
* `00_setup_environment.py`: Databricks notebook that initializes the database environment (market_project).
* `01_bronze_ingestion.py`: Notebook that imports data_ingestion and persists raw API data into Delta tables.
* `02_silver_transformation.py`: Formats and converts data types (strings to timestamps and numbers) to prepare data for analytics.
* `03_gold_transformation.py`: Window functions and financial metrics calculation.
* `04_data_quality_tests.py`: Computes final financial metrics (daily returns in percent and 7-day moving averages).

## Deployment & Automation
This project is orchestrated using **Databricks Workflows (Jobs)** and **Databricks Asset Bundles (DABs)**.

### Prerequisites
* Access to a Databricks workspace.
* API Key: Register for a free API key at [Alpha Vantage](https://www.alphavantage.co/).
* Store your key in a local file with the exact name `.env` (format: `ALPHA_VANTAGE_API_KEY=your_key_here`).

### How to Run
1. **Connect to Databricks**: Use Databricks Repos to link this GitHub repository.
2. **Deploy via CLI**:
   ```bash
   databricks bundle deploy