# InsightForge AI

Hey, this is a project I built to help small businesses upload messy datasets, understand what the columns mean, validate the file quality, and turn the data into useful sales and inventory KPIs.

I made it because real business files usually do not come with perfect column names. One spreadsheet might say `Sales_Volume`, another might say `Unit_Price`, `Qty`, `Stock_On_Hand`, or `SKU`. My goal was to make the app smart enough to separate sales from inventory, avoid bad mappings, and only show the metrics that actually exist in the file.

![1780709945758](image/README/1780709945758.png)

## What I built

- A FastAPI backend for dataset analysis and KPI generation
- A Streamlit dashboard for uploading files and exploring the results
- LLM-based column mapping with normalization rules for business datasets
- Data validation for empty columns, invalid numbers, and corrupt files
- Inventory-aware KPIs and charts alongside sales analytics
- Persisted metadata so each dataset remembers what was detected

![1780712135067](image/README/1780712135067.png)

## Stack

- FastAPI
- Streamlit
- Pandas
- SQLAlchemy
- Ollama for local LLM analysis
- SQLite by default for easy local testing

## Architecture

```mermaid
flowchart LR
    UI[Streamlit Dashboard] --> API[FastAPI]
    API --> ANALYSIS[LLM + Validation]
    ANALYSIS --> METADATA[(Dataset metadata)]
    API --> DB[(SQLite / PostgreSQL)]
    DB --> DASH[KPIs / Charts / Insights]
```

## What the app does

1. Upload a CSV or Excel file.
2. The API checks for empty columns, invalid numbers, and corrupted files.
3. The LLM proposes a normalized `column_mapping`.
4. The app detects the available KPIs and charts.
5. The dashboard renders only the metrics that make sense for that dataset.

## Features

- Sales and inventory column detection
- Safer mapping for fields like `Sales_Volume` and `Unit_Price`
- Inventory metrics like `total_stock`, `inventory_value`, and `stock_by_category`
- Charts for stock by category, location, supplier, and top products
- Clear error states when the dataset needs review
- Stored analysis metadata for every upload

## Public testing

I made the project easier to test from GitHub by defaulting the database to SQLite, so anyone can clone the repo and run it locally without setting up PostgreSQL first.

There are also some example datasets on the data folder , or you can use your own for testing!

For the full analysis experience, Ollama still needs to be running locally.

### Requirements

- Python 3.10+
- Ollama installed and running
- Optional: PostgreSQL if I want to override the default SQLite database

### Quick start

```bash
git clone https://github.com/<your-user>/sales-kpi-api.git
cd sales-kpi-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Run Ollama

```bash
ollama serve
ollama pull qwen2.5:14b
```

Note for Docker users on Windows/Mac: if you run `ollama serve` on your host, containers can reach it using `host.docker.internal`. The compose setup sets `OLLAMA_HOST=http://host.docker.internal:11434` for the API so it can call your local Ollama service.

### Run the API

```bash
uvicorn app.main:app --reload
```

### Run the dashboard

```bash
streamlit run dashboard.py
```

### Run with Docker Compose

```bash
docker compose up --build
```

Then open:

- API: http://localhost:8000
- Dashboard: http://localhost:8501

This is the easiest way for other people to test the project from GitHub because it starts both services with one command.

## API endpoints

- `POST /analyze-dataset`
- `POST /upload-dataset`
- `POST /upload-sales`
- `GET /datasets`
- `GET /datasets/{dataset_id}/dashboard`
- `GET /datasets/{dataset_id}/kpis`
- `GET /datasets/{dataset_id}/insights`
- `GET /kpi/revenue`
- `GET /kpi/top-products`

## Persisted metadata

Each dataset stores:

- `column_mapping`
- `detected_fields`
- `available_kpis`
- `available_charts`
- `validation_summary`

## Error messages

When the file is not reliable enough to analyze, it will show clear messages like:

- `No pude detectar KPIs`
- `El archivo no parece tener columnas numéricas`
- `Este dataset necesita revisión`

## Project structure

- `app/routes/` for API endpoints
- `app/services/` for shared analysis logic
- `app/models.py` for persistence
- `dashboard.py` for the Streamlit UI
- 

## Notes

If you want to use PostgreSQL instead of SQLite,  set `DATABASE_URL` before starting the app.

If you run the dashboard outside Docker, it uses `http://127.0.0.1:8000` by default. Inside Docker Compose, it points to the API service automatically.
