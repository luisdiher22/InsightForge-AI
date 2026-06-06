import json
import re
from ollama import chat


def clean_llm_json_response(content: str):
    content = re.sub(r"```json", "", content)
    content = re.sub(r"```", "", content)
    content = content.strip()

    return json.loads(content)


def generate_business_insights(dataset_type, business_description, kpis, charts):
    prompt = f"""
You are a business analytics consultant.

Analyze the following dashboard results and generate concise business insights.

Dataset type:
{dataset_type}

Business description:
{business_description}

KPIs:
{kpis}

Charts:
{charts}

Return ONLY valid JSON with this exact structure:

{{
  "insights": [
    "insight 1",
    "insight 2",
    "insight 3"
  ],
  "recommendations": [
    "recommendation 1",
    "recommendation 2"
  ]
}}

Rules:
- JSON only.
- Do not use markdown.
- Keep insights concise and business-friendly.
- Do not invent facts not supported by the KPIs or charts.
- Mention specific numbers when useful.
- Do not make recommendations that require data not available.
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

    content = response.message.content

    print("===== INSIGHTS LLM RESPONSE =====")
    print(content)
    print("=================================")

    return clean_llm_json_response(content)