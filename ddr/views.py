from django.shortcuts import render
from django.conf import settings
from pathlib import Path
import pandas as pd
import os
import re
from .service import report_logic


def ddr(request):
    directory_path = settings.BASE_DIR / "reports"
    reports = [report.name for report in directory_path.iterdir() if report.is_file()]

    return render(request, "ddr/ddr.html", {"reports": reports})


def temp(request, report):
    directory_path = settings.BASE_DIR / "reports"

    df_sales = pd.read_excel(report)

    # df_sales['Sales Person'] = '0'
    # df_sales['Branch'] = '0'

    # gstn_index = df_sales.columns.get_loc("Customer GSTN") + 1
    # df_sales.insert(gstn_index, 'Item Type', '0')

    df_parties = pd.read_excel(directory_path / "sub_reports" / "All_Parties_DDR.xlsx")
    # df_parties = df_parties.drop(['Branch'], axis=1)

    updated_sales = pd.merge(
        df_sales,
        df_parties[["GST", "Sales Person", "Branch"]],
        on="GST",
        how="inner",
    )

    updated_sales.to_excel(directory_path / "downloads/new.xlsx", index=False)

    # Merge DataFrames on 'Customer GSTN' and 'GST no'
    # Assuming 'Customer GSTN' and 'GST no' are the column names in both DataFrames
    # merged_df = pd.merge(df_parties, df_sales[['Customer GSTN', 'GST no', 'Sales Person']],
    #                      on=['Customer GSTN', 'GST no'],
    #                      how='left')

    report_excel = updated_sales.to_html(
        classes="table table-striped", index=False, header=True
    )






    updated_sales = updated_sales.groupby('Sales Person').agg({'Net Total': 'sum'}).reset_index()

    # Convert to HTML for displaying in the template
    analysis = updated_sales.to_html(classes="table table-striped", index=False, header=True)





    return render(
        request,
        "ddr/view_report.html",
        {
            "report": report.name,
            # "total": total,
            # "threshhold": threshhold,
            # "result": result,
            # "average": average,
            "report_excel": report_excel,
            "analysis": analysis,
        },
    )


def view_report(request, report):
    report = settings.BASE_DIR / "reports" / report

    if report.name == "Sale_Register_DDR.xlsx":
        return temp(request, report)

    # func = getattr(__service__, report.lower())

    # report_logic.func()

    # df = pd.read_excel(report, header=3, index_col=0)

    try:
        # total = df.at["Total", "Amount"]
        # df = pd.read_excel(report, header=3)
        # total_entries = df["Sr. No."].apply(lambda x: isinstance(x, (int, float))).sum()
        # threshhold = 30000
        # result = ""

        # match = re.search(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?", total)

        # if match:
        #     numerical_value = match.group(0).replace(",", "")
        #     numerical_value = float(numerical_value)
        # else:
        #     numerical_value = None

        # average = numerical_value / total_entries

        # df = pd.read_excel(report, header=None).drop(index=[0, 1, 2])
        df = pd.read_excel(report, header=3)
        report_excel = df.to_html(
            classes="table table-striped", index=False, header=False
        )

        # if average < threshhold:
        #     result = "Sales average low that the set threshhold"
        return render(
            request,
            "ddr/view_report.html",
            {
                "report": report.name,
                # "total": total,
                # "threshhold": threshhold,
                # "result": result,
                # "average": average,
                "report_excel": report_excel,
            },
        )
    except KeyError as e:
        print(f"Key error: {e} - Check if the specified row or column exists.")
