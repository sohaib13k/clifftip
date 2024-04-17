from django.shortcuts import render
from django.conf import settings
from pathlib import Path
import pandas as pd
import os
import re


def ddr(request):
    directory_path = settings.BASE_DIR + "reports"
    reports = [report.name for report in directory_path.iterdir() if report.is_file()]

    return render(request, "ddr/ddr.html", {"reports": reports})


def view_report(request, report):
    report = settings.BASE_DIR / "reports" / report
    df = pd.read_excel(report, header=3, index_col=0)

    try:
        total = df.at["Total", "Amount"]
        df = pd.read_excel(report, header=3)
        total_entries = df["Sr. No."].apply(lambda x: isinstance(x, (int, float))).sum()
        threshhold = 30000
        result = ""

        match = re.search(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?", total)

        if match:
            numerical_value = match.group(0).replace(",", "")
            numerical_value = float(numerical_value)
        else:
            numerical_value = None

        average = numerical_value / total_entries

        df = pd.read_excel(report, header=None).drop(index=[0, 1, 2])
        report_excel = df.to_html(
            classes="table table-striped", index=False, header=False
        )

        if average < threshhold:
            result = "Sales average low that the set threshhold"
        return render(
            request,
            "ddr/view_report.html",
            {
                "report": report,
                "total": total,
                "threshhold": threshhold,
                "result": result,
                "average": average,
                "report_excel": report_excel,
            },
        )
    except KeyError as e:
        print(f"Key error: {e} - Check if the specified row or column exists.")
