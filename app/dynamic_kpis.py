def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value):
    try:
        if value is None:
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _sum_field(data, field, converter):
    total = 0

    for row in data:
        value = converter(row.get(field))

        if value is not None:
            total += value

    return total


def calculate_dynamic_kpis(data, dataset_type=None):
    if not data:
        return {}

    dataset_type = (dataset_type or "").lower()

    if "inventory" in dataset_type:
        return calculate_inventory_kpis(data)

    if "sales" in dataset_type:
        return calculate_sales_kpis(data)

    return calculate_generic_kpis(data)


def calculate_sales_kpis(data):
    kpis = {}

    if all("revenue" in row for row in data):
        total_revenue = _sum_field(data, "revenue", _safe_float)
        kpis["total_revenue"] = total_revenue

    if all(any(field in row for field in ["quantity", "quantity_sold"]) for row in data):
        quantity_field = "quantity" if any("quantity" in row for row in data) else "quantity_sold"
        total_units = _sum_field(data, quantity_field, _safe_int)
        kpis["total_units_sold"] = total_units

    if "total_revenue" in kpis and len(data) > 0:
        kpis["average_sale_value"] = kpis["total_revenue"] / len(data)

    if all("category" in row and "revenue" in row for row in data):
        revenue_by_category = {}

        for row in data:
            category = row.get("category")
            revenue = row.get("revenue")

            if category is not None and revenue is not None:
                revenue_by_category[category] = (
                    revenue_by_category.get(category, 0) + float(revenue)
                )

        kpis["revenue_by_category"] = revenue_by_category

    if all(("product" in row or "product_id" in row) and "revenue" in row for row in data):
        revenue_by_product = {}

        for row in data:
            product = row.get("product") or row.get("product_id")
            revenue = row.get("revenue")

            if product is not None and revenue is not None:
                revenue_by_product[product] = (
                    revenue_by_product.get(product, 0) + float(revenue)
                )

        sorted_products = sorted(
            revenue_by_product.items(),
            key=lambda item: item[1],
            reverse=True
        )

        kpis["top_products_by_revenue"] = dict(sorted_products[:5])

    return kpis


def calculate_inventory_kpis(data):
    kpis = {}

    if all(any(field in row for field in ["quantity", "quantity_sold"]) for row in data):
        quantity_field = "quantity" if any("quantity" in row for row in data) else "quantity_sold"
        total_stock = _sum_field(data, quantity_field, _safe_int)

        kpis["total_stock"] = total_stock

    if all(any(field in row for field in ["quantity", "quantity_sold"]) and any(cost_field in row for cost_field in ["cost", "unit_price"]) for row in data):
        inventory_value = sum(
            (_safe_int(row.get("quantity") if row.get("quantity") is not None else row.get("quantity_sold")) or 0)
            * (_safe_float(row.get("cost")) if row.get("cost") is not None else (_safe_float(row.get("unit_price")) or 0))
            for row in data
            if (row.get("quantity") is not None or row.get("quantity_sold") is not None)
            and (row.get("cost") is not None or row.get("unit_price") is not None)
        )

        kpis["inventory_value"] = inventory_value

    if all("category" in row and any(field in row for field in ["quantity", "quantity_sold"]) for row in data):
        stock_by_category = {}

        for row in data:
            category = row.get("category")
            quantity = row.get("quantity") if row.get("quantity") is not None else row.get("quantity_sold")

            if category is not None and quantity is not None:
                stock_by_category[category] = (
                    stock_by_category.get(category, 0) + (_safe_int(quantity) or 0)
                )

        kpis["stock_by_category"] = stock_by_category

    if all("location" in row and any(field in row for field in ["quantity", "quantity_sold"]) for row in data):
        stock_by_location = {}

        for row in data:
            location = row.get("location")
            quantity = row.get("quantity") if row.get("quantity") is not None else row.get("quantity_sold")

            if location is not None and quantity is not None:
                stock_by_location[location] = (
                    stock_by_location.get(location, 0) + (_safe_int(quantity) or 0)
                )

        kpis["stock_by_location"] = stock_by_location

    if all(("product" in row or "product_id" in row) and any(field in row for field in ["quantity", "quantity_sold"]) for row in data):
        stock_by_product = {}

        for row in data:
            product = row.get("product") or row.get("product_id")
            quantity = row.get("quantity") if row.get("quantity") is not None else row.get("quantity_sold")

            if product is not None and quantity is not None:
                stock_by_product[product] = (
                    stock_by_product.get(product, 0) + (_safe_int(quantity) or 0)
                )

        sorted_products = sorted(
            stock_by_product.items(),
            key=lambda item: item[1],
            reverse=True
        )

        kpis["top_products_by_stock"] = dict(sorted_products[:5])

    return kpis


def calculate_generic_kpis(data):
    kpis = {}

    numeric_fields = []

    first_row = data[0]

    for field, value in first_row.items():
        try:
            float(value)
            numeric_fields.append(field)
        except (TypeError, ValueError):
            pass

    for field in numeric_fields:
        total = 0

        for row in data:
            value = row.get(field)

            if value is not None:
                try:
                    total += float(value)
                except (TypeError, ValueError):
                    pass

        kpis[f"total_{field}"] = total

    return kpis