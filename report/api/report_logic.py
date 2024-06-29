from django.utils import timezone
from django.core.cache import cache
from report.models import Report
import pandas as pd
from django.http import JsonResponse
import os
from django.conf import settings
from commonutil import commonutil
from report.commonutil import append_total, add_percentage_column


def sale_purchase(request, report, filtered_data):
    # Aggregating sales values
    individual_sales = (
        filtered_data.groupby("Sales Person").agg({"Net Total": "sum"}).reset_index()
    )
    individual_sales = append_total(individual_sales, "Sales Person", "Net Total")
    individual_sales = add_percentage_column(individual_sales, "Net Total")

    branch_sales = (
        filtered_data.groupby("Branch").agg({"Net Total": "sum"}).reset_index()
    )
    branch_sales = append_total(branch_sales, "Branch", "Net Total")
    branch_sales = add_percentage_column(branch_sales, "Net Total")

    item_type_sales = (
        filtered_data.groupby("Item Type").agg({"Net Total": "sum"}).reset_index()
    )
    item_type_sales = append_total(item_type_sales, "Item Type", "Net Total")
    item_type_sales = add_percentage_column(item_type_sales, "Net Total")

    # import locale
    # locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
    #
    # def format_currency(value):
    #     return locale.format_string("%d", value, grouping=True)

    # item_type_sales = append_total(item_type_sales, "Item Type", "Net Total")
    # item_type_sales['Net Total'] = item_type_sales['Net Total'].apply(format_currency)

    individual_by_item_type_sales = (
        filtered_data.groupby(["Sales Person", "Item Type"])
        .agg({"Net Total": "sum"})
        .unstack(fill_value=0)
    )

    branch_by_item_type_sales = (
        filtered_data.groupby(["Branch", "Item Type"])
        .agg({"Net Total": "sum"})
        .unstack(fill_value=0)
    )

    # formatting numbers as per locale
    # format_currency

    individual_sales["Net Total"] = (
        individual_sales["Net Total"]
        .round()
        .astype(int)
        .apply(commonutil.format_rupees)
    )
    branch_sales["Net Total"] = (
        branch_sales["Net Total"].round().astype(int).apply(commonutil.format_rupees)
    )
    item_type_sales["Net Total"] = (
        item_type_sales["Net Total"].round().astype(int).apply(commonutil.format_rupees)
    )

    for column in individual_by_item_type_sales.columns:  # Skip the first column
        individual_by_item_type_sales[column] = (
            individual_by_item_type_sales[column]
            .round()
            .astype(int)
            .apply(commonutil.format_rupees)
        )

    for column in branch_by_item_type_sales.columns:  # Skip the first column
        branch_by_item_type_sales[column] = (
            branch_by_item_type_sales[column]
            .round()
            .astype(int)
            .apply(commonutil.format_rupees)
        )

    # Convert to HTML for displaying in the template
    sales_analysis = individual_sales.to_html(
        classes="table table-striped", index=False, header=True
    )
    branch_analysis = branch_sales.to_html(
        classes="table table-striped", index=False, header=True
    )
    item_type_analysis = item_type_sales.to_html(
        classes="table table-striped", index=False, header=True
    )
    individual_by_item_type_analysis = individual_by_item_type_sales.to_html(
        classes="table table-striped", index=True, header=True
    )
    branch_by_item_type_analysis = branch_by_item_type_sales.to_html(
        classes="table table-striped", index=True, header=True
    )

    result = {
        "sales_analysis": sales_analysis,
        "branch_analysis": branch_analysis,
        "item_type_analysis": item_type_analysis,
        "individual_by_item_type_analysis": individual_by_item_type_analysis,
        "branch_by_item_type_analysis": branch_by_item_type_analysis,
    }

    return result


def all_parties_with_sale(request, report, parties_with_sale):
    sale_reg_csv_dir = settings.CSV_DIR / "sale_register"
    sale_register_model = Report.objects.get(service_name='sale_register')
    all_parties_model = Report.objects.get(service_name='all_parties') # TODO: replace this with all_parties_with_sale
    cache_key = 'all_parties_with_sale_cache222'
    cache_tmstmp_key = 'all_parties_with_sale_cache_tmstmpqwqw'
    cache_exist = False

    # Check if the result is already cached and if the cache is up-to-date
    cache_tmstmp = cache.get(cache_tmstmp_key)
    if cache_tmstmp and cache_tmstmp > max(sale_register_model.report_last_updated_tmstmp, all_parties_model.report_last_updated_tmstmp):
        result = cache.get(cache_key)
        if result is not None:
            cache_exist = True

    if not cache_exist:
        try:
            df_sales = pd.DataFrame()
            for filename in os.listdir(sale_reg_csv_dir):
                if filename.endswith(".csv"):
                    file_path = os.path.join(sale_reg_csv_dir, filename)
                    df = pd.read_csv(file_path)
                    df_sales = pd.concat([df_sales, df], ignore_index=True)

            df_sales["Invoice Date"] = pd.to_datetime(df_sales["Invoice Date"])

            result = []
            for index, row in parties_with_sale.iterrows():
                customer_name = row["Company Name"]
                branch = row["Branch.1"]
                sales_person = row["Sales Person"]
                gst_no = row["GST No."]

                sales_data = df_sales[df_sales["Customer GSTN"] == gst_no]

                if not sales_data.empty:
                    first_sale = sales_data["Invoice Date"].min()
                    result.append(
                        {
                            "name": customer_name if pd.notna(customer_name) else "",
                            "branch": branch if pd.notna(branch) else "",
                            "person": sales_person if pd.notna(sales_person) else "",
                            "gst": gst_no if pd.notna(gst_no) else "",
                            "first_sale": (
                                first_sale.strftime("%Y-%m-%d") if pd.notna(first_sale) else ""
                            ),
                        }
                    )

            # Cache the result for future use
            cache.set(cache_key, result)
            cache.set(cache_tmstmp_key, timezone.now())

        except FileNotFoundError:
            return JsonResponse(
                {"error": "CSV file not found"},
                status=406,
            )

    return result


def invoice_report(request, report, filtered_data):
    if filtered_data.empty or len(filtered_data) == 0:
        return {
            "less_than_zero": {"count": 0, "percentage": 0},
            "zero": {"count": 0, "percentage": 0},
            "one": {"count": 0, "percentage": 0},
            "more_than_one": {"count": 0, "percentage": 0},
            "cond_1": {"top": 0, "bottom": 0},
            "cond_2": {"top": 0, "bottom": 0},
        }

    less_than_zero = len(filtered_data[filtered_data["Delay Shipment Days"] < 0])
    zero = len(filtered_data[filtered_data["Delay Shipment Days"] == 0])
    one = len(filtered_data[filtered_data["Delay Shipment Days"] == 1])
    more_than_one = len(filtered_data[filtered_data["Delay Shipment Days"] > 1])
    delay_sum = filtered_data["Delay Shipment Days"].sum()
    net_avg = filtered_data["Net Shipment Days"].mean()

    total_count = len(filtered_data)

    percent_less_than_zero = (less_than_zero / total_count) * 100
    percent_zero = (zero / total_count) * 100
    percent_one = (one / total_count) * 100
    percent_more_than_one = (more_than_one / total_count) * 100

    results = {
        "less_than_zero": {
            "count": less_than_zero,
            "percentage": percent_less_than_zero,
        },
        "zero": {"count": zero, "percentage": percent_zero},
        "one": {"count": one, "percentage": percent_one},
        "more_than_one": {"count": more_than_one, "percentage": percent_more_than_one},
        "cond_1": {
            "top": percent_less_than_zero + percent_zero,
            "bottom": percent_one + percent_more_than_one,
        },
        "cond_2": {
            "top": percent_less_than_zero + percent_zero + percent_one,
            "bottom": percent_more_than_one,
        },
        "delay_sum": delay_sum,
        "net_avg": net_avg,
    }

    return results
