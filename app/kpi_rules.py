def _has_any(fields, *candidates):
    return any(candidate in fields for candidate in candidates)


def get_available_kpis(dataset_type, fields):

    dataset_type = dataset_type.lower()

    if "inventory" in dataset_type:
        return inventory_kpis(fields)

    if "sales" in dataset_type:
        return sales_kpis(fields)

    return generic_kpis(fields)


def get_available_charts(dataset_type, fields):

    dataset_type = dataset_type.lower()

    if "inventory" in dataset_type:
        return inventory_charts(fields)

    if "sales" in dataset_type:
        return sales_charts(fields)

    return generic_charts(fields)

def sales_kpis(fields):

    kpis = []

    if _has_any(fields, "revenue"):
        kpis.append("total_revenue")

    if _has_any(fields, "revenue"):
        kpis.append("average_sale_value")

    if _has_any(fields, "quantity", "quantity_sold"):
        kpis.append("total_units_sold")

    if _has_any(fields, "product", "product_id") and _has_any(fields, "revenue"):
        kpis.append("top_products_by_revenue")

    if _has_any(fields, "product", "product_id") and _has_any(fields, "quantity", "quantity_sold"):
        kpis.append("top_products_by_quantity")

    if "category" in fields and _has_any(fields, "revenue"):
        kpis.append("revenue_by_category")

    if "date" in fields and _has_any(fields, "revenue"):
        kpis.append("revenue_over_time")

    if "seller" in fields and _has_any(fields, "revenue"):
        kpis.append("revenue_by_seller")

    if _has_any(fields, "revenue") and _has_any(fields, "cost"):
        kpis.append("estimated_profit")

    if _has_any(fields, "unit_price") and _has_any(fields, "quantity", "quantity_sold"):
        kpis.append("average_unit_price")

    return kpis

def sales_charts(fields):

    charts = []

    if "category" in fields and _has_any(fields, "revenue"):
        charts.append("bar_chart_revenue_by_category")

    if _has_any(fields, "product", "product_id") and _has_any(fields, "revenue"):
        charts.append("bar_chart_top_products_by_revenue")

    if _has_any(fields, "product", "product_id") and _has_any(fields, "quantity", "quantity_sold"):
        charts.append("bar_chart_top_products_by_quantity")

    if "date" in fields and _has_any(fields, "revenue"):
        charts.append("line_chart_revenue_over_time")

    if "seller" in fields and _has_any(fields, "revenue"):
        charts.append("bar_chart_revenue_by_seller")

    if _has_any(fields, "unit_price") and _has_any(fields, "quantity", "quantity_sold"):
        charts.append("line_chart_average_unit_price")

    return charts

def inventory_kpis(fields):

    kpis = []

    if _has_any(fields, "quantity", "quantity_sold"):
        kpis.append("total_stock")

    if _has_any(fields, "quantity", "quantity_sold") and _has_any(fields, "cost", "unit_price"):
        kpis.append("inventory_value")

    if _has_any(fields, "product", "product_id") and _has_any(fields, "quantity", "quantity_sold"):
        kpis.append("top_products_by_stock")

    if "category" in fields and _has_any(fields, "quantity", "quantity_sold"):
        kpis.append("stock_by_category")

    if "location" in fields and _has_any(fields, "quantity", "quantity_sold"):
        kpis.append("stock_by_location")

    if "supplier" in fields:
        kpis.append("supplier_count")

    if "unit_price" in fields:
        kpis.append("average_unit_price")

    return kpis

def inventory_charts(fields):

    charts = []

    if "category" in fields and _has_any(fields, "quantity", "quantity_sold"):
        charts.append("bar_chart_stock_by_category")

    if _has_any(fields, "product", "product_id") and _has_any(fields, "quantity", "quantity_sold"):
        charts.append("bar_chart_top_products_by_stock")

    if "location" in fields and _has_any(fields, "quantity", "quantity_sold"):
        charts.append("bar_chart_stock_by_location")

    if "supplier" in fields and _has_any(fields, "quantity", "quantity_sold"):
        charts.append("bar_chart_stock_by_supplier")

    return charts

def generic_kpis(fields):

    kpis = []

    numeric_fields = [
        f for f in fields
        if f in ["quantity", "quantity_sold", "revenue", "cost", "unit_price"]
    ]

    for field in numeric_fields:
        kpis.append(f"total_{field}")

    return kpis

def generic_charts(fields):
    return []