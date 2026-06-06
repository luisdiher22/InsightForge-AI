from fastapi import APIRouter, HTTPException
from sqlalchemy import func

from app.database import SessionLocal
from app.dynamic_kpis import calculate_dynamic_kpis
from app.models import Dataset, DatasetRow, Sale


router = APIRouter(tags=["kpis"])


@router.get("/kpi/revenue")
def total_revenue():
    db = SessionLocal()

    try:
        total_revenue_value = db.query(func.sum(Sale.revenue)).scalar()
        return {"total_revenue": total_revenue_value}
    finally:
        db.close()


@router.get("/kpi/category-sales")
def sales_by_category():
    db = SessionLocal()

    try:
        results = (
            db.query(
                Sale.category,
                func.sum(Sale.revenue),
            )
            .group_by(Sale.category)
            .all()
        )

        return results
    finally:
        db.close()


@router.get("/kpi/top-products")
def top_products():
    db = SessionLocal()

    try:
        results = (
            db.query(
                Sale.product,
                func.sum(Sale.revenue).label("total_revenue"),
            )
            .group_by(Sale.product)
            .order_by(func.sum(Sale.revenue).desc())
            .limit(5)
            .all()
        )

        return results
    finally:
        db.close()


@router.get("/kpi/units-sold")
def total_units_sold():
    db = SessionLocal()

    try:
        total_units = db.query(func.sum(Sale.quantity)).scalar()
        return {"total_units_sold": total_units}
    finally:
        db.close()


@router.get("/kpi/average-sale")
def average_sale():
    db = SessionLocal()

    try:
        avg_sale = db.query(func.avg(Sale.revenue)).scalar()
        return {"average_sale_revenue": avg_sale}
    finally:
        db.close()


@router.get("/kpi/best-selling-product")
def best_selling_product():
    db = SessionLocal()

    try:
        result = (
            db.query(
                Sale.product,
                func.sum(Sale.quantity).label("units_sold"),
            )
            .group_by(Sale.product)
            .order_by(func.sum(Sale.quantity).desc())
            .first()
        )

        return result
    finally:
        db.close()


@router.get("/datasets/{dataset_id}/kpis")
def get_dataset_kpis(dataset_id: int):
    db = SessionLocal()

    try:
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

        return {
            "dataset_id": dataset_id,
            "dataset_type": dataset.dataset_type,
            "rows_analyzed": len(data),
            "kpis": kpis,
        }
    finally:
        db.close()