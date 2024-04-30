import pandas as pd


def get_excel_read_engine(excel_path):
    """Read Excel file using appropriate engine based on file extension."""
    return "openpyxl" if excel_path.suffix == ".xlsx" else "xlrd"


def sale_purchase(excel_path):
    return pd.read_excel(
        excel_path, engine=get_excel_read_engine(excel_path), skiprows=3
    )


def all_parties(excel_path):
    return pd.read_excel(excel_path, engine=get_excel_read_engine(excel_path))
