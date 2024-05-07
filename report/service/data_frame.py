import pandas as pd
from commonutil.commonutil import read_excel_or_html


def default(excel_path):
    return read_excel_or_html(excel_path)


def sale_register(excel_path):
    return read_excel_or_html(excel_path, skiprows=3)


def all_parties(excel_path):
    return read_excel_or_html(excel_path)


def item_type_finished_goods(excel_path):
    return read_excel_or_html(excel_path)


def routing_report(excel_path):
    return read_excel_or_html(excel_path)


def bom_report(excel_path):
    return read_excel_or_html(excel_path)


def sale_purchase(excel_path):
    return read_excel_or_html(excel_path)
