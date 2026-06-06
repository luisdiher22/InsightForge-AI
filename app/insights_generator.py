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
You are an experienced business analytics consultant writing to a commercial audience (managers and operations leads).

Analyze the following dashboard results and produce a concise, professional, and prioritized set of business insights and short recommendations.

Dataset type:
{dataset_type}

Business description:
{business_description}

KPIs (dictionary):
{kpis}

Charts (list or dict):
{charts}

Return ONLY valid JSON with this exact structure:

{{
  "insights": [
    "insight 1",
    "insight 2"
  ],
  "recommendations": [
    "recommendation 1",
    "recommendation 2"
  ]
}}

Formatting and content rules:
- JSON only, no markdown, no extra keys.
- Provide up to 5 insights and up to 5 recommendations, prioritized (most important first).
- Each insight should be one sentence, professional tone, and may include a brief numeric example (e.g., "Average unit price is $12.50, 20% below category average"). Do not invent external benchmarks.
- Each recommendation should be a short action-oriented sentence and may include an estimated priority tag in brackets at the end like "[High]", "[Medium]", or "[Low]".
- Prefer concrete, testable actions (e.g., "Investigate SKU X for price variance", "Reconcile supplier Y stock levels").
- Do not make claims that cannot be supported by the provided KPIs or charts. When uncertain, phrase as a suggested check ("Verify...", "Investigate...").
- Keep language formal and business-focused; avoid casual phrases.

If data is limited and no confident insight can be produced, return an empty `insights` list and a short recommendation to improve data quality.
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