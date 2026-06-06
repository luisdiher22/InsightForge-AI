import json
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional

import pandas as pd
from ollama import chat

from app.kpi_rules import get_available_charts, get_available_kpis


ALLOWED_FIELDS = [
    "date",
    "product",
    "product_id",
    "category",
    "quantity",
    "quantity_sold",
    "revenue",
    "unit_price",
    "cost",
    "customer",
    "seller",
    "supplier",
    "supplier_id",
    "location",
    "payment_method",
    "order_id",
    "stock",
]

FIELD_RULES = [
    (re.compile(r"(?i)\b(sales?_?volume|qty|quantity|units?_?sold|items?_?sold|stock)\b"), "quantity_sold"),
    (re.compile(r"(?i)\b(unit[_\s]*price|price[_\s]*per[_\s]*unit|price[_\s]*each|unitprice)\b"), "unit_price"),
    (re.compile(r"(?i)\b(cost|purchase\s*cost|unit\s*cost|expense|costo)\b"), "cost"),
    (re.compile(r"(?i)\b(product\s*id|sku|item\s*id|article\s*id)\b"), "product_id"),
    (re.compile(r"(?i)\b(supplier\s*id|vendor\s*id)\b"), "supplier_id"),
    (re.compile(r"(?i)\b(supplier|vendor|provider)\b"), "supplier"),
    (re.compile(r"(?i)\b(warehouse|store|branch|aisle|location|site)\b"), "location"),
    (re.compile(r"(?i)\b(category|segment|department|group)\b"), "category"),
    (re.compile(r"(?i)\b(date|day|month|year|timestamp|created_at|order_date)\b"), "date"),
    (re.compile(r"(?i)\b(customer|client|buyer)\b"), "customer"),
    (re.compile(r"(?i)\b(seller|salesperson|rep|agent)\b"), "seller"),
    (re.compile(r"(?i)\b(payment\s*method|payment|channel)\b"), "payment_method"),
    (re.compile(r"(?i)\b(order\s*id|invoice\s*id|transaction\s*id)\b"), "order_id"),
    (re.compile(r"(?i)\b(revenue|sales\s*amount|amount\s*sold|total\s*sales|turnover|income)\b"), "revenue"),
]

NUMERIC_HINTS = re.compile(
    r"(?i)\b(quantity|qty|units?|sold|volume|revenue|sales|amount|price|cost|value|stock|balance|total|count)\b"
)

IDENTIFIER_HINTS = re.compile(r"(?i)\b(id|code|sku|key|uuid)\b")


def clean_llm_json_response(content: str) -> Dict[str, Any]:
    content = re.sub(r"```json", "", content)
    content = re.sub(r"```", "", content)
    content = content.strip()

    if not content.startswith("{"):
        match = re.search(r"\{.*\}", content, re.S)
        if match:
            content = match.group(0)

    return json.loads(content)


def _normalize_field_name(original_column: str, proposed_field: Optional[str]) -> Optional[str]:
    original_lower = str(original_column).strip().lower()

    for pattern, field_name in FIELD_RULES:
        if pattern.search(original_lower):
            return field_name

    if proposed_field is None:
        return None

    normalized = str(proposed_field).strip().lower()

    if normalized not in ALLOWED_FIELDS:
        return None

    return normalized


def normalize_column_mapping(
    raw_mapping: Mapping[str, Any],
    columns: Optional[Iterable[str]] = None,
) -> Dict[str, str]:
    normalized_mapping: Dict[str, str] = {}
    ordered_columns = list(columns or raw_mapping.keys())

    for column in ordered_columns:
        proposed_field = raw_mapping.get(column)
        normalized_field = _normalize_field_name(column, proposed_field)

        if normalized_field:
            normalized_mapping[column] = normalized_field

    return normalized_mapping


def _build_prompt(columns, sample_rows):
    return f"""
You are a business intelligence and data engineering assistant.

Analyze this uploaded business dataset.

CSV Columns:
{columns}

Sample Rows:
{sample_rows}

Your task:
1. Identify what type of business dataset this is.
2. Map the original columns to a normalized schema.
3. Identify which normalized fields are available.

Use these normalized field names when they fit the data:
- date
- product
- product_id
- category
- quantity
- quantity_sold
- revenue
- unit_price
- cost
- customer
- seller
- supplier
- supplier_id
- location
- payment_method
- order_id
- stock

Important mapping rules:
- Sales_Volume, Units_Sold, Qty and similar fields must NOT be mapped to revenue.
- Prefer quantity_sold or quantity for sold units.
- Unit_Price must NOT be assumed to be cost.
- Use unit_price when the column is a unit price.
- Use cost only when the column clearly represents cost, purchase cost, or expense.
- Support inventory datasets with supplier, product_id, stock, and location fields.

Return ONLY valid JSON with this exact structure:

{{
  "dataset_type": "short_dataset_type",
  "business_description": "short explanation",
  "column_mapping": {{
    "original_column_name": "normalized_field_name"
  }},
  "detected_fields": [
    "normalized_field_name"
  ]
}}

Important:
- JSON only.
- The keys in column_mapping MUST be the original CSV column names.
- The values in column_mapping MUST be normalized field names.
- detected_fields MUST only include fields that exist after mapping.
- Do not include markdown.
- Do not include explanations outside JSON.
"""


def infer_column_mapping(columns, sample_rows=None):
    prompt = _build_prompt(columns, sample_rows)

    response = chat(
        model="qwen2.5:14b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    content = response.message.content

    print("===== COLUMN MAPPING LLM RESPONSE =====")
    print(content)
    print("======================================")

    raw_mapping = clean_llm_json_response(content)
    return normalize_column_mapping(raw_mapping, columns=columns)


def analyze_dataset_with_llm(columns, sample_rows):
    prompt = _build_prompt(columns, sample_rows)

    response = chat(
        model="qwen2.5:14b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    content = response.message.content

    print("===== DATASET ANALYSIS LLM RESPONSE =====")
    print(content)
    print("=========================================")
    analysis = clean_llm_json_response(content)

    raw_mapping = analysis.get("column_mapping", {})
    mapping = normalize_column_mapping(raw_mapping, columns=columns)

    analysis["column_mapping"] = mapping
    analysis["detected_fields"] = [
        field for field in dict.fromkeys(mapping.values())
        if field in ALLOWED_FIELDS
    ]

    dataset_type = analysis.get("dataset_type", "")
    detected_fields = analysis["detected_fields"]

    analysis["available_kpis"] = get_available_kpis(dataset_type, detected_fields)
    analysis["available_charts"] = get_available_charts(dataset_type, detected_fields)

    return analysis


def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    issues: List[str] = []
    warnings: List[str] = []
    empty_columns: List[str] = []
    numeric_columns: List[str] = []
    invalid_numeric_cells: Dict[str, int] = {}
    useful_numeric_columns: List[str] = []

    if df is None or df.empty:
        return {
            "status": "needs_review",
            "analysis_message": "Este dataset necesita revisión",
            "issues": ["empty_dataset"],
            "warnings": [],
            "empty_columns": [],
            "numeric_columns": [],
            "useful_numeric_columns": [],
            "invalid_numeric_cells": {},
            "has_numeric_columns": False,
            "has_useful_metrics": False,
        }

    for column in df.columns:
        column_name = str(column).strip()
        series = df[column]
        non_empty = series.dropna().astype(str).str.strip()

        if not column_name:
            empty_columns.append("<empty column name>")
            continue

        if non_empty.empty:
            empty_columns.append(column_name)
            continue

        is_numeric_hint = bool(NUMERIC_HINTS.search(column_name))
        is_identifier = bool(IDENTIFIER_HINTS.search(column_name))

        numeric_series = pd.to_numeric(non_empty, errors="coerce")
        valid_count = int(numeric_series.notna().sum())
        invalid_count = int(len(non_empty) - valid_count)

        if valid_count > 0 and (is_numeric_hint or series.dtype.kind in "if" or valid_count / len(non_empty) >= 0.5):
            numeric_columns.append(column_name)

            if not is_identifier:
                useful_numeric_columns.append(column_name)

            if invalid_count > 0:
                invalid_numeric_cells[column_name] = invalid_count

        elif is_numeric_hint and valid_count == 0 and invalid_count > 0:
            invalid_numeric_cells[column_name] = invalid_count

    if empty_columns:
        issues.append("empty_columns")

    if invalid_numeric_cells:
        issues.append("invalid_numbers")

    has_numeric_columns = bool(numeric_columns)
    has_useful_metrics = bool(useful_numeric_columns)

    if not has_numeric_columns:
        issues.append("no_numeric_columns")
        warnings.append("El archivo no parece tener columnas numéricas")

    if not has_useful_metrics:
        issues.append("no_kpis")
        warnings.append("No pude detectar KPIs")

    if issues:
        warnings.append("Este dataset necesita revisión")

    status = "ready" if not issues else "needs_review"

    if not warnings:
        analysis_message = "Dataset listo"
    elif "El archivo no parece tener columnas numéricas" in warnings:
        analysis_message = "El archivo no parece tener columnas numéricas"
    elif "No pude detectar KPIs" in warnings:
        analysis_message = "No pude detectar KPIs"
    else:
        analysis_message = "Este dataset necesita revisión"

    return {
        "status": status,
        "analysis_message": analysis_message,
        "issues": issues,
        "warnings": list(dict.fromkeys(warnings)),
        "empty_columns": empty_columns,
        "numeric_columns": numeric_columns,
        "useful_numeric_columns": useful_numeric_columns,
        "invalid_numeric_cells": invalid_numeric_cells,
        "has_numeric_columns": has_numeric_columns,
        "has_useful_metrics": has_useful_metrics,
    }


def inspect_dataset_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    analysis = analyze_dataset_with_llm(
        columns=list(df.columns),
        sample_rows=df.head(5).to_dict(orient="records"),
    )

    validation = validate_dataframe(df)

    analysis["validation_summary"] = validation
    analysis["analysis_status"] = validation["status"]
    analysis["analysis_message"] = validation["analysis_message"]

    return analysis