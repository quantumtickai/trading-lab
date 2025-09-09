# trading-lab

A fully automated, data-driven trading system using tick-by-tick data, real-time pipelines, and QLib-based backtesting.

## Structure

quantumtickai/
├── .github/
│   └── workflows/        # GitHub Actions (later)
├── api/                  # APIs for data access or serving models
├── backtest/             # QLib workflows, custom strategy engines
├── data/                 # Only metadata or sample (NOT full data)
├── docs/                 # Architecture docs, guides, runbooks
├── ingest/               # Scripts to pull/download raw data
├── lake/                 # Table format definitions (Delta/Iceberg)
├── normalize/            # Clean + standardize raw data to Parquet
├── orchestration/        # Airflow or Prefect workflows
├── quality/              # Great Expectations data quality checks
├── research/             # Notebooks, experiments, strategy ideas
├── infra/                # Terraform, IaC, AWS provisioning (later)
├── .gitignore
├── README.md
├── environment.yml       # Conda env (optional)


## Goal

Build a high-performance, collaborative algo-trading platform focused on scientific rigor and repeatable, risk-adjusted returns.