def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _sum_by_field(data, group_field, value_fields):
    grouped = {}

    for row in data:
        group_value = row.get(group_field)

        if group_value is None:
            continue

        numeric_value = None

        for value_field in value_fields:
            numeric_value = _safe_float(row.get(value_field))

            if numeric_value is not None:
                break

        if numeric_value is None:
            continue

        grouped[group_value] = grouped.get(group_value, 0) + numeric_value

    return grouped


def _build_bar_chart(data_map):
    sorted_items = sorted(data_map.items(), key=lambda item: item[1], reverse=True)

    return {
        "type": "bar",
        "labels": [item[0] for item in sorted_items],
        "values": [item[1] for item in sorted_items],
    }


def generate_chart_data(data, dataset_type=None):
    charts = {}

    if all("category" in row and "revenue" in row for row in data):
        charts["revenue_by_category"] = _build_bar_chart(
            _sum_by_field(data, "category", ["revenue"])
        )

    if all(("product" in row or "product_id" in row) and "revenue" in row for row in data):
        revenue_by_product = _sum_by_field(data, "product", ["revenue"])

        if not revenue_by_product:
            revenue_by_product = _sum_by_field(data, "product_id", ["revenue"])

        charts["top_products_by_revenue"] = _build_bar_chart(
            dict(sorted(revenue_by_product.items(), key=lambda item: item[1], reverse=True)[:5])
        )

    if all(("product" in row or "product_id" in row) and any(field in row for field in ["quantity", "quantity_sold"]) for row in data):
        stock_by_product = _sum_by_field(data, "product", ["quantity", "quantity_sold"])

        if not stock_by_product:
            stock_by_product = _sum_by_field(data, "product_id", ["quantity", "quantity_sold"])

        charts["top_products_by_stock"] = _build_bar_chart(
            dict(sorted(stock_by_product.items(), key=lambda item: item[1], reverse=True)[:5])
        )

    if all("category" in row and any(field in row for field in ["quantity", "quantity_sold"]) for row in data):
        charts["stock_by_category"] = _build_bar_chart(
            _sum_by_field(data, "category", ["quantity", "quantity_sold"])
        )

    if all("location" in row and any(field in row for field in ["quantity", "quantity_sold"]) for row in data):
        charts["stock_by_location"] = _build_bar_chart(
            _sum_by_field(data, "location", ["quantity", "quantity_sold"])
        )

    if all("supplier" in row and any(field in row for field in ["quantity", "quantity_sold"]) for row in data):
        charts["stock_by_supplier"] = _build_bar_chart(
            _sum_by_field(data, "supplier", ["quantity", "quantity_sold"])
        )

    return charts