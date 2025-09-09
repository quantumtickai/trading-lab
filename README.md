# trading-lab

A fully automated, data-driven trading system using tick-by-tick data, real-time pipelines, and QLib-based backtesting.

## Structure

- `ingest/` – data ingestion scripts (real-time & batch)
- `normalize/` – cleaning + standardizing raw data
- `lake/` – Delta/Iceberg tables
- `backtest/` – QLib pipelines and custom strategy logic
- `research/` – notebooks and experiments
- `infra/` – Terraform code for AWS setup


## Goal

Build a high-performance, collaborative algo-trading platform focused on scientific rigor and repeatable, risk-adjusted returns.