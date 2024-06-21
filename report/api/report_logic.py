from commonutil import commonutil
from report.commonutil import append_total, add_percentage_column


def sale_purchase(request, report, filtered_data):
    item_type_sales = (
        filtered_data.groupby("Item Type").agg({"Net Total": "sum"}).reset_index()
    )
    item_type_sales = append_total(item_type_sales, "Item Type", "Net Total")
    item_type_sales = add_percentage_column(item_type_sales, "Net Total")

    item_type_sales["Net Total"] = item_type_sales["Net Total"].apply(
        commonutil.format_rupees
    )

    item_type_analysis = item_type_sales.to_html(
         index=False, header=True
    )

    result = {"item_type_analysis": item_type_analysis}

    return result
