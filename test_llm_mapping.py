import unittest

import pandas as pd

from app.services.analysis_service import normalize_column_mapping, validate_dataframe


class AnalysisServiceTests(unittest.TestCase):
    def test_sales_volume_is_not_mapped_to_revenue(self):
        mapping = normalize_column_mapping(
            {
                "Sales_Volume": "revenue",
                "Unit_Price": "cost",
                "Product ID": "product",
            },
            columns=["Sales_Volume", "Unit_Price", "Product ID"],
        )

        self.assertEqual(mapping["Sales_Volume"], "quantity_sold")
        self.assertEqual(mapping["Unit_Price"], "unit_price")
        self.assertEqual(mapping["Product ID"], "product_id")

    def test_validation_flags_invalid_numbers_and_missing_metrics(self):
        dataframe = pd.DataFrame(
            {
                "product": ["A", "B"],
                "quantity": ["10", "bad"],
                "notes": ["ok", "ok"],
            }
        )

        validation = validate_dataframe(dataframe)

        self.assertEqual(validation["status"], "needs_review")
        self.assertIn("invalid_numbers", validation["issues"])
        self.assertIn("quantity", validation["invalid_numeric_cells"])


if __name__ == "__main__":
    unittest.main()
from ollama import chat

columns = [
    "Artículo",
    "Cantidad Vendida",
    "Monto Facturado"
]

prompt = f"""
You are a data engineer.

Map the following columns to this schema:

Schema:
- product
- quantity
- revenue

Columns:
{columns}

Return ONLY valid JSON.

Example:

{{
    "Artículo": "product",
    "Cantidad Vendida": "quantity",
    "Monto Facturado": "revenue"
}}
"""

response = chat(
    model="qwen2.5:14b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print(response.message.content)