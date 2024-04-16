from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import os
from django.conf import settings
import re


def ddrweb(request):
    directory_path = os.path.join(settings.BASE_DIR, "reports")

    reports = [
        f
        for f in os.listdir(directory_path)
        if os.path.isfile(os.path.join(directory_path, f))
    ]

    return render(request, "ddrweb/ddrweb.html", {"reports": reports})


def viewReport(request, fileName):
    filename = os.path.join(settings.BASE_DIR, "reports", fileName)
    df = pd.read_excel(filename, header=3, index_col=0)

    try:
        total = df.at["Total", "Amount"]
        df = pd.read_excel(filename, header=3)
        total_entries = df["Sr. No."].apply(lambda x: isinstance(x, (int, float))).sum()
        threshhold = 3000
        result = ""

        # total_cleaned = re.findall("\d+", total)
        # joined_number = "".join(str(num) for num in total_cleaned)

        match = re.search(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?", total)

        # If a match is found, replace commas and convert to float
        if match:
            numerical_value = match.group(0).replace(",", "")
            numerical_value = float(
                numerical_value
            )  # Convert string to float if necessary
        else:
            numerical_value = None

        average = numerical_value / total_entries
        print(">>>>>>>>>>>>>>>", average, total_entries)

        if average < threshhold:
            result = "Sales average low that the set threshhold"
            return render(
                request,
                "ddrweb/viewReport.html",
                {
                    "total": total,
                    "threshhold": threshhold,
                    "result": result,
                    "average": average,
                },
            )
        else:
            return render(
                request,
                "ddrweb/viewReport.html",
                {
                    "total": total,
                    "threshhold": threshhold,
                    "result": result,
                    "average": average,
                },
            )
    except KeyError as e:
        print(f"Key error: {e} - Check if the specified row or column exists.")
