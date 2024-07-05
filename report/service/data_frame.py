import pandas as pd
from commonutil.commonutil import read_excel_or_html, remove_trailing_non_numeric


def default(excel_path):
    return read_excel_or_html(excel_path)[0]


def sale_register(excel_path):
    df, is_html = read_excel_or_html(excel_path, skiprows=3)

    if not is_html:
        return df

    for i in df:
        # TODO: Remove this hard coding and get from report.date_col
        if "Invoice Date" in i.columns:
            df = remove_trailing_non_numeric(i)
            return df

    return None


def all_parties(excel_path):
    return read_excel_or_html(excel_path)[0]


def item_type_finished_goods(excel_path):
    return read_excel_or_html(excel_path)[0]


def routing_report(excel_path):
    return read_excel_or_html(excel_path)[0]


def bom_report(excel_path):
    return read_excel_or_html(excel_path)[0]


def sale_purchase(excel_path):
    return read_excel_or_html(excel_path)[0]


def invoice_report(excel_path):
    df, is_html = read_excel_or_html(excel_path, skiprows=3)

    if not is_html:
        return df

    for i in df:
        # TODO: Remove this hard coding and get from report.date_col
        if "Invoice Date" in i.columns:
            return remove_trailing_non_numeric(i)

    return None


def pending_sales_order(excel_path):
    df, is_html = read_excel_or_html(excel_path, header=1)

    if not is_html:
        df.drop(columns=[df.columns[0]], inplace=True)
        df.rename(columns={"Unnamed: 22": "VALUE.2"}, inplace=True)
        return df

    df = df[0]
    return df.drop(df.index[-1]).drop(
        columns=[df.columns[0], df.columns[-1], df.columns[-2]]
    )


def cnf_charges(excel_path):
    df = read_excel_or_html(excel_path, skiprows=2)[0]
    df['Date'] = df['Date'].fillna(method='ffill')
    df.drop(df.index[-1], inplace=True)
    return df