import os

import requests
import pandas as pd
import streamlit as st

from file_utils import load_dataframe


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


st.set_page_config(
    page_title="InsightForge AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
<style>
:root {
    --bg: #07111f;
    --bg-soft: #0c1727;
    --bg-card: rgba(10, 18, 32, 0.88);
    --bg-card-2: rgba(13, 24, 42, 0.92);
    --border: rgba(148, 163, 184, 0.18);
    --border-strong: rgba(148, 163, 184, 0.28);
    --text: #e5eef9;
    --muted: #92a4bc;
    --accent: #6ee7ff;
    --accent-2: #8b5cf6;
    --success: #22c55e;
    --warning: #f59e0b;
    --danger: #ef4444;
}

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, rgba(110, 231, 255, 0.16), transparent 35%),
        radial-gradient(circle at 85% 12%, rgba(139, 92, 246, 0.18), transparent 30%),
        linear-gradient(180deg, #050b14 0%, #07111f 38%, #07111f 100%);
    color: var(--text);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(7, 17, 31, 0.98), rgba(10, 20, 38, 0.96));
    border-right: 1px solid var(--border);
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

.hero {
    display: grid;
    grid-template-columns: 1.8fr 1fr;
    gap: 18px;
    align-items: stretch;
    padding: 22px;
    border-radius: 28px;
    border: 1px solid var(--border-strong);
    background:
        radial-gradient(circle at top right, rgba(110, 231, 255, 0.12), transparent 28%),
        radial-gradient(circle at bottom left, rgba(139, 92, 246, 0.14), transparent 26%),
        linear-gradient(135deg, rgba(10, 18, 32, 0.92), rgba(7, 16, 30, 0.88));
    box-shadow: 0 28px 80px rgba(0, 0, 0, 0.25);
    margin-bottom: 1rem;
}

.hero-title {
    font-size: 48px;
    line-height: 1.0;
    font-weight: 900;
    letter-spacing: -0.04em;
    margin: 0 0 10px 0;
}

.hero-subtitle {
    color: var(--muted);
    font-size: 17px;
    max-width: 62ch;
    margin-bottom: 16px;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 999px;
    border: 1px solid rgba(110, 231, 255, 0.22);
    background: rgba(110, 231, 255, 0.08);
    color: var(--accent);
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 14px;
}

.hero-panel {
    border-radius: 22px;
    border: 1px solid var(--border);
    background: linear-gradient(180deg, rgba(15, 24, 42, 0.9), rgba(8, 16, 30, 0.96));
    padding: 18px;
}

.hero-panel h4 {
    margin: 0 0 10px 0;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
}

.hero-metric {
    margin-bottom: 12px;
    padding: 14px 16px;
    border-radius: 18px;
    border: 1px solid var(--border);
    background: rgba(255, 255, 255, 0.03);
}

.hero-metric-label {
    color: var(--muted);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 6px;
}

.hero-metric-value {
    color: var(--text);
    font-size: 26px;
    font-weight: 800;
    line-height: 1;
}

.hero-metric-note {
    color: var(--muted);
    font-size: 12px;
    margin-top: 6px;
}

.dashboard-card {
    border-radius: 20px;
    border: 1px solid var(--border);
    background: linear-gradient(180deg, rgba(13, 24, 42, 0.94), rgba(9, 17, 31, 0.96));
    padding: 18px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.16);
}

.dashboard-card.soft {
    background: linear-gradient(180deg, rgba(10, 18, 32, 0.8), rgba(9, 16, 30, 0.9));
}

.card-title {
    color: var(--muted);
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 10px;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
}

.kpi-card {
    border-radius: 18px;
    border: 1px solid var(--border);
    background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
    padding: 16px;
    min-height: 122px;
}

.kpi-label {
    color: var(--muted);
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.11em;
}

.kpi-value {
    color: #ffffff;
    font-size: 32px;
    font-weight: 900;
    line-height: 1.05;
    margin-top: 12px;
}

.kpi-subtext {
    color: var(--muted);
    font-size: 12px;
    margin-top: 8px;
}

.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 12px 0 0 0;
}

.pill {
    padding: 8px 12px;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: rgba(255,255,255,0.03);
    color: var(--text);
    font-size: 12px;
    font-weight: 700;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border: 1px solid var(--border);
    background: rgba(255,255,255,0.03);
    color: var(--text);
}

.status-ready { color: #bbf7d0; border-color: rgba(34, 197, 94, 0.35); background: rgba(34, 197, 94, 0.08); }
.status-review { color: #fde68a; border-color: rgba(245, 158, 11, 0.35); background: rgba(245, 158, 11, 0.08); }
.status-alert { color: #fecaca; border-color: rgba(239, 68, 68, 0.35); background: rgba(239, 68, 68, 0.08); }

.section-heading {
    margin: 0 0 12px 0;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: -0.02em;
}

.muted {
    color: var(--muted);
}

.grid-2 {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}

.grid-3 {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
}

.quality-item {
    padding: 14px 16px;
    border-radius: 16px;
    border: 1px solid var(--border);
    background: rgba(255, 255, 255, 0.03);
    margin-bottom: 12px;
}

.quality-label {
    color: var(--muted);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 6px;
}

.quality-value {
    color: var(--text);
    font-size: 18px;
    font-weight: 800;
}

.info-banner {
    padding: 16px 18px;
    border-radius: 18px;
    border: 1px solid var(--border);
    background: rgba(255,255,255,0.03);
    color: var(--text);
}

.empty-state {
    padding: 24px;
    border-radius: 22px;
    border: 1px dashed rgba(148, 163, 184, 0.26);
    background: rgba(255,255,255,0.03);
}
</style>
""",
    unsafe_allow_html=True,
)


def safe_text(text):
    return str(text).replace("$", "\\$")


def get_dashboard(dataset_id):
    response = requests.get(f"{API_BASE_URL}/datasets/{dataset_id}/dashboard")

    if response.status_code == 200:
        return response.json()

    try:
        error = response.json().get("detail", response.text)
    except ValueError:
        error = response.text

    return {"error": error}


def get_insights(dataset_id):
    response = requests.get(f"{API_BASE_URL}/datasets/{dataset_id}/insights")

    if response.status_code == 200:
        return response.json()

    try:
        error = response.json().get("detail", response.text)
    except ValueError:
        error = response.text

    return {"error": error}


def render_metric_card(label, value, note=None):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {f'<div class="kpi-subtext">{note}</div>' if note else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_kpi_value(key, value):
    if isinstance(value, (int, float)):
        if any(token in key for token in ["revenue", "value", "price", "cost"]):
            return f"${value:,.2f}"

        return f"{value:,.0f}"

    return str(value)


def render_breakdown_table(key, value):
    st.markdown(f"#### {key.replace('_', ' ').title()}")
    breakdown_df = pd.DataFrame({"Item": list(value.keys()), "Value": list(value.values())})
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)


def render_chart_card(chart_name, chart):
    chart_df = pd.DataFrame({"Label": chart["labels"], "Value": chart["values"]})

    st.markdown(
        f"""
        <div class="dashboard-card soft">
            <div class="card-title">{chart_name.replace('_', ' ').title()}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.bar_chart(chart_df, x="Label", y="Value", use_container_width=True)


def render_status_pill(status):
    status_value = (status or "").lower()

    if status_value == "ready":
        return '<span class="status-pill status-ready">Ready</span>'

    if status_value == "needs_review":
        return '<span class="status-pill status-review">Needs Review</span>'

    return '<span class="status-pill status-alert">Attention</span>'


def render_empty_home():
    st.markdown(
        """
        <div class="hero">
            <div>
                <div class="eyebrow">InsightForge AI</div>
                <div class="hero-title">A dashboard that reads like a product, not a form.</div>
                <div class="hero-subtitle">
                    Upload business data and get a responsive executive view with KPIs, charts, validation signals,
                    and AI insights for sales and inventory datasets.
                </div>
                <div class="pill-row">
                    <div class="pill">Sales and inventory aware</div>
                    <div class="pill">LLM column mapping</div>
                    <div class="pill">Validation before analysis</div>
                    <div class="pill">Metadata persisted</div>
                </div>
            </div>
            <div class="hero-panel">
                <h4>What you get</h4>
                <div class="hero-metric">
                    <div class="hero-metric-label">Executive KPIs</div>
                    <div class="hero-metric-value">Sales + Inventory</div>
                    <div class="hero-metric-note">Cards adapt to the dataset instead of hard-coding revenue only.</div>
                </div>
                <div class="hero-metric">
                    <div class="hero-metric-label">Quality Signals</div>
                    <div class="hero-metric-value">Review aware</div>
                    <div class="hero-metric-note">Flags empty columns, invalid values, and weak datasets early.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_recent_datasets():
    response = requests.get(f"{API_BASE_URL}/datasets")

    if response.status_code == 200:
        return response.json()

    return []


def render_dashboard(dashboard):
    kpis = dashboard.get("kpis", {})
    charts = dashboard.get("charts", {})
    validation = dashboard.get("validation_summary", {}) or {}
    status_message = validation.get("analysis_message") or dashboard.get("message")
    detected_fields = dashboard.get("detected_fields", []) or []
    available_kpis = dashboard.get("available_kpis", []) or []
    available_charts = dashboard.get("available_charts", []) or []

    st.markdown(
        f"""
        <div class="hero">
            <div>
                <div class="eyebrow">InsightForge AI</div>
                <div class="hero-title">{dashboard['filename']}</div>
                <div class="hero-subtitle">{dashboard['business_description']}</div>
                <div class="pill-row">
                    <div class="pill">Dataset type: {dashboard['dataset_type']}</div>
                    <div class="pill">Rows: {dashboard['rows_analyzed']}</div>
                    <div class="pill">Detected fields: {len(detected_fields)}</div>
                    <div class="pill">Charts: {len(available_charts)}</div>
                </div>
            </div>
            <div class="hero-panel">
                <h4>Analysis status</h4>
                <div class="info-banner">
                    {render_status_pill(validation.get('status'))}
                    <div style="margin-top: 12px; font-size: 17px; font-weight: 800;">{status_message or 'Dataset ready'}</div>
                    <div class="muted" style="margin-top: 6px;">Metadata saved: column mapping, detected fields, KPIs, charts, and validation summary.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    overview_tab, charts_tab, insights_tab, quality_tab, metadata_tab = st.tabs(
        ["Overview", "Charts", "Insights", "Quality", "Metadata"]
    )

    scalar_kpis = {
        key: value
        for key, value in kpis.items()
        if not isinstance(value, (dict, list))
    }

    breakdown_items = {
        key: value
        for key, value in kpis.items()
        if isinstance(value, dict) and value
    }

    with overview_tab:
        st.markdown('<div class="section-heading">Executive Summary</div>', unsafe_allow_html=True)

        if scalar_kpis:
            kpi_columns = st.columns(4)

            for index, (key, value) in enumerate(scalar_kpis.items()):
                with kpi_columns[index % 4]:
                    render_metric_card(
                        key.replace("_", " ").title(),
                        format_kpi_value(key, value),
                        note="Dynamic KPI",
                    )
        else:
            st.warning("No pude detectar KPIs")

        if breakdown_items:
            st.markdown('<div class="section-heading" style="margin-top: 18px;">Breakdowns</div>', unsafe_allow_html=True)
            breakdown_columns = st.columns(min(2, len(breakdown_items)))

            for index, (key, value) in enumerate(breakdown_items.items()):
                with breakdown_columns[index % len(breakdown_columns)]:
                    render_breakdown_table(key, value)

    with charts_tab:
        st.markdown('<div class="section-heading">Visual Analysis</div>', unsafe_allow_html=True)

        if not charts:
            st.info("Este dataset necesita revisión")
        else:
            chart_items = list(charts.items())

            for index in range(0, len(chart_items), 2):
                left_col, right_col = st.columns(2)
                pair = chart_items[index:index + 2]

                for column, (chart_name, chart) in zip([left_col, right_col], pair):
                    with column:
                        render_chart_card(chart_name, chart)

    with insights_tab:
        st.markdown('<div class="section-heading">AI Business Insights</div>', unsafe_allow_html=True)

        with st.spinner("Generating AI insights..."):
            insights_data = get_insights(dashboard["dataset_id"])

        if insights_data and not insights_data.get("error"):
            insights = insights_data.get("insights", [])
            recommendations = insights_data.get("recommendations", [])

            insight_col, rec_col = st.columns(2)

            with insight_col:
                st.markdown('<div class="dashboard-card"><div class="card-title">Key Insights</div></div>', unsafe_allow_html=True)

                if insights:
                    for insight in insights:
                        st.info(safe_text(insight))
                else:
                    st.write("No insights generated.")

            with rec_col:
                st.markdown('<div class="dashboard-card"><div class="card-title">Recommendations</div></div>', unsafe_allow_html=True)

                if recommendations:
                    for recommendation in recommendations:
                        st.success(safe_text(recommendation))
                else:
                    st.write("No recommendations generated.")
        else:
            st.warning("Could not generate insights.")

    with quality_tab:
        st.markdown('<div class="section-heading">Data Quality</div>', unsafe_allow_html=True)

        quality_cols = st.columns(3)
        quality_cols[0].markdown(
            f"""
            <div class="quality-item">
                <div class="quality-label">Status</div>
                <div class="quality-value">{validation.get('status', 'unknown')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        quality_cols[1].markdown(
            f"""
            <div class="quality-item">
                <div class="quality-label">Numeric columns</div>
                <div class="quality-value">{len(validation.get('numeric_columns', []))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        quality_cols[2].markdown(
            f"""
            <div class="quality-item">
                <div class="quality-label">Invalid numeric cells</div>
                <div class="quality-value">{sum(validation.get('invalid_numeric_cells', {}).values())}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if validation.get("empty_columns"):
            st.warning(f"Empty columns: {', '.join(validation['empty_columns'])}")

        if validation.get("invalid_numeric_cells"):
            st.warning(f"Invalid numeric values detected in: {', '.join(validation['invalid_numeric_cells'].keys())}")

        st.json(validation)

    with metadata_tab:
        st.markdown('<div class="section-heading">Persisted Metadata</div>', unsafe_allow_html=True)
        metadata_cols = st.columns(2)

        with metadata_cols[0]:
            st.write("Available KPIs")
            st.write(available_kpis)
            st.write("Available Charts")
            st.write(available_charts)

        with metadata_cols[1]:
            st.write("Detected Fields")
            st.write(detected_fields)
            st.write("Column Mapping")
            st.json(dashboard.get("column_mapping", {}))

    st.caption("Dashboard updated from the latest uploaded dataset.")


def render_app_shell():
    st.sidebar.markdown(
        '<div class="dashboard-card"><div class="card-title">InsightForge AI</div><div style="font-size:24px;font-weight:900;line-height:1.1;">Analytics Studio</div><div class="muted" style="margin-top:8px;">Sales, inventory, and AI-generated insights.</div></div>',
        unsafe_allow_html=True,
    )

    recent_datasets = load_recent_datasets()

    st.sidebar.markdown("### Recent Datasets")

    if recent_datasets:
        for dataset in recent_datasets:
            label = f"{dataset['filename']} · ID {dataset['id']}"

            if st.sidebar.button(label, use_container_width=True):
                selected_dashboard = get_dashboard(dataset["id"])

                if selected_dashboard and not selected_dashboard.get("error"):
                    st.session_state["dashboard"] = selected_dashboard
                else:
                    st.sidebar.error("Could not load dashboard.")
    else:
        st.sidebar.info("No datasets yet.")

    st.sidebar.divider()
    st.sidebar.markdown("### Upload Flow")
    st.sidebar.markdown("1. Select a CSV or XLSX file\n2. Generate the dashboard\n3. Review quality and insights")

    st.markdown(
        """
        <div class="hero">
            <div>
                <div class="eyebrow">InsightForge AI</div>
                <div class="hero-title">Executive analytics for messy business files.</div>
                <div class="hero-subtitle">
                    Upload a dataset and let the app infer the right schema, validate quality, and surface a dashboard
                    that adapts to sales or inventory signals.
                </div>
                <div class="pill-row">
                    <div class="pill">Dynamic KPI selection</div>
                    <div class="pill">Inventory support</div>
                    <div class="pill">Quality-first analysis</div>
                    <div class="pill">Persistent metadata</div>
                </div>
            </div>
            <div class="hero-panel">
                <h4>Highlights</h4>
                <div class="hero-metric">
                    <div class="hero-metric-label">Coverage</div>
                    <div class="hero-metric-value">Sales + Stock</div>
                    <div class="hero-metric-note">Supports total stock, inventory value, location and category breakdowns.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="dashboard-card"><div class="card-title">New Analysis</div></div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

        if uploaded_file is not None:
            preview_df = load_dataframe(uploaded_file)

            with st.expander("Preview uploaded file", expanded=False):
                st.dataframe(preview_df.head(12), use_container_width=True, hide_index=True)

            uploaded_file.seek(0)

            if st.button("Generate Dashboard", type="primary", use_container_width=True):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file,
                        "application/octet-stream",
                    )
                }

                with st.spinner("Analyzing dataset with AI..."):
                    upload_response = requests.post(f"{API_BASE_URL}/upload-dataset", files=files)

                if upload_response.status_code != 200:
                    try:
                        error_payload = upload_response.json()
                        error_message = error_payload.get("detail", upload_response.text)
                    except ValueError:
                        error_message = upload_response.text

                    st.error(error_message)
                else:
                    upload_data = upload_response.json()
                    dataset_id = upload_data["dataset_id"]

                    dashboard = get_dashboard(dataset_id)

                    if dashboard and not dashboard.get("error"):
                        st.session_state["dashboard"] = dashboard
                        st.success("Dashboard generated successfully.")
                    else:
                        st.error("Could not load dashboard.")

    if "dashboard" in st.session_state:
        st.divider()
        render_dashboard(st.session_state["dashboard"])
    else:
        st.info("Sube un archivo para generar KPIs y gráficos dinámicos.")


render_app_shell()