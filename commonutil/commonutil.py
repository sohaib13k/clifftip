from typing import List, Union
from django.db.models.query import QuerySet
import numpy as np
import random
import string
from datetime import datetime, timedelta
from django.conf import settings
import os
from babel.numbers import format_decimal
import pandas as pd
from pathlib import Path
from report.models import Report

def uploaded_excel(f, location):
    """
    save excel file at specified location. Directory will be created recursivly if not exists

    :param location: location where write need to be done
    """
    if not os.path.exists(location):
        os.makedirs(location, exist_ok=True)

    with open(location / f.name, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def get_unique_filename():
    today_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_str = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{today_str}_{random_str}"


def format_rupees(number):
    try:
        return format_decimal(number, locale="en_IN")
    except:
        return number


def get_interval_date_str(interval):
    """
    Return start date and end date from a given interval.
    start date is assumed the past date and end date is closer to todays date

    returns (start date, end date)
    start date = YYYY-mm-dd
    end date = YYYY-mm-dd
    """
    now = datetime.now().today()

    if interval == "day":
        # TODO: this in unncecessary as already by default one month data in been sent, so fetch from that
        return (now.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d"))
    elif interval == "week":
        start_date = now - timedelta(now.weekday())
        return (start_date.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d"))
    elif interval == "month":
        return (
            "-".join(map(lambda x: str(x).zfill(2), [now.year, now.month, 1])),
            now.strftime("%Y-%m-%d"),
        )
    elif interval == "year":
        return (
            "-".join(map(lambda x: str(x).zfill(2), [now.year, 1, 1])),
            now.strftime("%Y-%m-%d"),
        )


def read_excel_or_html(excel_path, skiprows=None, header=None):
    """
    Reads an Excel file or converts an HTML file to a DataFrame.
    :param excel_path: Path of the file to be read.
    :param skiprows: Number of rows to skip at the start of the file for Excel files.
    :return: A DataFrame containing the data.
    """
    if is_file_html(excel_path):
        if header:
            return pd.read_html(excel_path, header=[header]), True
        else:
            return pd.read_html(excel_path), True
    return pd.read_excel(
        excel_path, engine=get_excel_read_engine(excel_path), skiprows=skiprows
    ), False


def is_file_html(file_path):
    """Check if the file content starts with typical HTML tags."""
    try:
        with open(file_path, "rb") as file:
            start = file.read(100).decode("utf-8").strip()
            return (
                start.startswith("<!DOCTYPE") or "<html" in start or "<table" in start
            )
    except Exception as e:
        return False


def get_excel_read_engine(excel_path):
    """Read Excel file using appropriate engine based on file extension."""
    return "openpyxl" if excel_path.suffix == ".xlsx" else "xlrd"


def rename_file_with_unique_suffix(
    file_path,
    filename,
    data_basedir,
    report=None,
):
    ext = Path(filename).suffix
    unique_suffix = get_unique_filename()
    new_path = (
        Path(data_basedir)
        / report.service_name
        / f"{Path(filename).stem}_{unique_suffix}.bak{ext}"
    )
    file_path.rename(new_path)


def get_latest_csv_from_dir(report):
    csv_dir = settings.CSV_DIR / report.service_name
    try:
        latest_file = max(csv_dir.glob("*.csv"), key=lambda x: x.stat().st_mtime)
    except ValueError:
        return None

    return latest_file


def remove_trailing_non_numeric(df):
    """Removed extra rows at the end of an excel, like 'Total' or 'Amount in words:'
    """
    for idx in range(len(df) - 1, -1, -1):
        if pd.notna(pd.to_numeric(df.iloc[idx, 0], errors='coerce')):
            break
    return df.iloc[:idx + 1]


def remove_trailing_decimal(value):
    """
    Remove the trailing decimal from a value if it is an integer.
    
    This function checks if the provided value is an integer (i.e., has a .0 decimal part).
    If so, it returns the value as an integer. If the value has a non-zero decimal part,
    it returns the value unchanged. It also handles NaN values by returning an empty string.
    
    Parameters:
    value (float or int): The value to be processed.
    
    Returns:
    int, float, or str: The integer value if the input was a whole number, 
                        otherwise the original float value or an empty string for NaN.
    """
    if isinstance(value, str):
        return
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return int(value)
    else:
        return value
    
def convert_numpy_types(d):
    for key, value in d.items():
        if isinstance(value, dict):
            convert_numpy_types(value)
        elif isinstance(value, np.int64):
            d[key] = int(value)
        elif isinstance(value, np.float64):
            d[key] = float(value)


def extract_upload_from_custom_report(
    param1: Union["Report", QuerySet["Report"]], 
    result_list: List["Report"]
) -> List["Report"]:
    """
    Extracts all non-custom Report instances from a report queryset and appends them to a result list.

    Args:
        param1: A report queryset which could be a single Report instance or a QuerySet of Report instances.
        result_list: A list to which non-custom Report instances will be appended.

    Returns:
        list: The result_list with appended non-custom Report instances.
    """
    if isinstance(param1, Report):
        if not param1.is_custom_report:
            if param1 not in result_list:
                result_list.append(param1)
            return result_list
        else:
            return extract_upload_from_custom_report(param1.reports.all(), result_list)

    for report in param1:
        result_list = extract_upload_from_custom_report(report, result_list)

    return result_list
