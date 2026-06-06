from fastapi import APIRouter, File, HTTPException, UploadFile
import pandas as pd

from app.database import SessionLocal
from app.file_utils import load_dataframe
from app.models import Dataset, DatasetRow, Sale
from app.services.analysis_service import inspect_dataset_dataframe


router = APIRouter(tags=["uploads"])


def _prepare_dataset_record(file_name, analysis):
    return Dataset(
        filename=file_name,
        dataset_type=analysis.get("dataset_type"),
        business_description=analysis.get("business_description"),
        column_mapping=analysis.get("column_mapping"),
        detected_fields=analysis.get("detected_fields"),
        available_kpis=analysis.get("available_kpis"),
        available_charts=analysis.get("available_charts"),
        validation_summary=analysis.get("validation_summary"),
    )


def _persist_dataset_rows(db, dataset_id, dataframe):
    for _, row in dataframe.iterrows():
        clean_row = row.where(pd.notnull(row), None).to_dict()

        dataset_row = DatasetRow(
            dataset_id=dataset_id,
            row_data=clean_row,
        )

        db.add(dataset_row)


@router.post("/analyze-dataset")
async def analyze_dataset(file: UploadFile = File(...)):
    try:
        dataframe = load_dataframe(file.file, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    analysis = inspect_dataset_dataframe(dataframe)

    return {
        "status": analysis.get("analysis_status", "needs_review"),
        "message": analysis.get("analysis_message"),
        "dataset_type": analysis.get("dataset_type"),
        "business_description": analysis.get("business_description"),
        "column_mapping": analysis.get("column_mapping"),
        "detected_fields": analysis.get("detected_fields"),
        "available_kpis": analysis.get("available_kpis"),
        "available_charts": analysis.get("available_charts"),
        "validation_summary": analysis.get("validation_summary"),
    }


@router.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        dataframe = load_dataframe(file.file, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    analysis = inspect_dataset_dataframe(dataframe)
    dataframe = dataframe.rename(columns=analysis.get("column_mapping", {}))
    dataset = _prepare_dataset_record(file.filename, analysis)

    db = SessionLocal()

    try:
        db.add(dataset)
        db.commit()
        db.refresh(dataset)

        _persist_dataset_rows(db, dataset.id, dataframe)
        db.commit()

        return {
            "status": analysis.get("analysis_status", "needs_review"),
            "message": analysis.get("analysis_message"),
            "dataset_id": dataset.id,
            "filename": file.filename,
            "dataset_type": analysis.get("dataset_type"),
            "detected_fields": analysis.get("detected_fields"),
            "available_kpis": analysis.get("available_kpis"),
            "available_charts": analysis.get("available_charts"),
            "validation_summary": analysis.get("validation_summary"),
            "rows_uploaded": len(dataframe),
            "column_mapping": analysis.get("column_mapping"),
        }
    finally:
        db.close()


@router.post("/upload-sales")
async def upload_sales(file: UploadFile = File(...)):
    try:
        dataframe = load_dataframe(file.file, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    analysis = inspect_dataset_dataframe(dataframe)
    mapping = analysis.get("column_mapping", {})
    dataframe = dataframe.rename(columns=mapping)

    product_column = "product" if "product" in dataframe.columns else "product_id" if "product_id" in dataframe.columns else None

    if not product_column:
        raise HTTPException(status_code=422, detail="No pude detectar KPIs")

    quantity_column = "quantity" if "quantity" in dataframe.columns else "quantity_sold" if "quantity_sold" in dataframe.columns else None

    if "revenue" not in dataframe.columns and not (quantity_column and "unit_price" in dataframe.columns):
        raise HTTPException(status_code=422, detail="No pude detectar KPIs")

    db = SessionLocal()

    try:
        for _, row in dataframe.iterrows():
            quantity_value = row.get(quantity_column) if quantity_column else None
            revenue_value = row.get("revenue")

            if revenue_value is None and quantity_value is not None and row.get("unit_price") is not None:
                try:
                    revenue_value = float(quantity_value) * float(row.get("unit_price"))
                except (TypeError, ValueError):
                    revenue_value = None

            sale = Sale(
                product=row.get(product_column),
                category=row.get("category") if "category" in dataframe.columns else None,
                quantity=int(float(quantity_value)) if quantity_value is not None else 0,
                revenue=float(revenue_value) if revenue_value is not None else 0.0,
            )

            db.add(sale)

        db.commit()
    finally:
        db.close()

    return {
        "status": analysis.get("analysis_status", "needs_review"),
        "message": analysis.get("analysis_message"),
        "rows_uploaded": len(dataframe),
        "dataset_type": analysis.get("dataset_type"),
        "detected_fields": analysis.get("detected_fields"),
        "column_mapping": mapping,
    }