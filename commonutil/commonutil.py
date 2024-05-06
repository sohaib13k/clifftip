import random
import string
from datetime import datetime, timedelta
import os
from babel.numbers import format_decimal
import pandas as pd
from pathlib import Path


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


def read_excel_or_html(excel_path, skiprows=None):
    """
    Reads an Excel file or converts an HTML file to a DataFrame.
    :param excel_path: Path of the file to be read.
    :param skiprows: Number of rows to skip at the start of the file for Excel files.
    :return: A DataFrame containing the data.
    """
    if is_file_html(excel_path):
        # Convert HTML to DataFrame if the file is HTML
        return convert_html_to_dataframe(excel_path)
    # Otherwise, read as Excel file
    return pd.read_excel(
        excel_path, engine=get_excel_read_engine(excel_path), skiprows=skiprows
    )


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


def convert_html_to_dataframe(html_path):
    """Convert an HTML file to a DataFrame and return it.

    This function reads an HTML file, assuming it contains at least one table,
    and returns the first table as a DataFrame.
    """
    # Use Pandas to read the HTML file
    df_list = pd.read_html(html_path)
    # Assuming the first table is what you need
    return df_list[0]  # Return the DataFrame of the first table directly


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
