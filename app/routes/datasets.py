from fastapi import APIRouter, HTTPException

from app.database import SessionLocal
from app.dynamic_charts import generate_chart_data
from app.dynamic_kpis import calculate_dynamic_kpis
from app.insights_generator import generate_business_insights
from app.models import Dataset, DatasetRow


router = APIRouter(tags=["datasets"])


def _load_dataset_payload(db, dataset_id):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    rows = (
        db.query(DatasetRow)
        .filter(DatasetRow.dataset_id == dataset_id)
        .all()
    )

    data = [row.row_data for row in rows]
    kpis = calculate_dynamic_kpis(data, dataset.dataset_type)
    charts = generate_chart_data(data, dataset.dataset_type)

    return dataset, data, kpis, charts


@router.get("/datasets")
def list_datasets():
    db = SessionLocal()

    try:
        datasets = (
            db.query(Dataset)
            .order_by(Dataset.uploaded_at.desc())
            .all()
        )

        return [
            {
                "id": dataset.id,
                "filename": dataset.filename,
                "dataset_type": dataset.dataset_type,
                "business_description": dataset.business_description,
                "uploaded_at": dataset.uploaded_at,
                "validation_summary": dataset.validation_summary,
            }
            for dataset in datasets
        ]
    finally:
        db.close()


@router.get("/datasets/{dataset_id}/dashboard")
def get_dataset_dashboard(dataset_id: int):
    db = SessionLocal()

    try:
        dataset, data, kpis, charts = _load_dataset_payload(db, dataset_id)

        return {
            "dataset_id": dataset_id,
            "filename": dataset.filename,
            "dataset_type": dataset.dataset_type,
            "business_description": dataset.business_description,
            "rows_analyzed": len(data),
            "kpis": kpis,
            "charts": charts,
            "column_mapping": dataset.column_mapping,
            "detected_fields": dataset.detected_fields,
            "available_kpis": dataset.available_kpis or list(kpis.keys()),
            "available_charts": dataset.available_charts or list(charts.keys()),
            "validation_summary": dataset.validation_summary,
        }
    finally:
        db.close()


@router.get("/datasets/{dataset_id}/insights")
def get_dataset_insights(dataset_id: int):
    db = SessionLocal()

    try:
        dataset, data, kpis, charts = _load_dataset_payload(db, dataset_id)

        insights = generate_business_insights(
            dataset_type=dataset.dataset_type,
            business_description=dataset.business_description,
            kpis=kpis,
            charts=charts,
        )

        return {
            "dataset_id": dataset_id,
            "dataset_type": dataset.dataset_type,
            "insights": insights.get("insights", []),
            "recommendations": insights.get("recommendations", []),
        }
    finally:
        db.close()