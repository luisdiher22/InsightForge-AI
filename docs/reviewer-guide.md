# Reviewer Guide

This project is meant to be easy to review from GitHub.

## Fastest way to try it

```bash
docker compose up --build
```

Then open:

- http://localhost:8000
- http://localhost:8501

## What to test

1. Upload `data/test_sales.csv`.
2. Confirm the dashboard shows sales KPIs and charts.
3. Upload an inventory dataset and confirm inventory KPIs appear.
4. Upload a broken, empty, or non-numeric file and confirm the validation message is clear.
5. Check that the README explains the setup without needing extra context.

## What this project demonstrates

- LLM-assisted column mapping with guardrails
- Inventory-aware analytics
- Data validation and user-friendly errors
- FastAPI router structure
- Streamlit dashboard design
- Docker-based local testing
