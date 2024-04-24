import pandas as pd
from babel.numbers import format_currency, format_decimal


def append_total(*args):
    """
    Returns data_frame with a row appended with label 'Total' showing the sum of second column
    """
    total_net = args[0][args[2]].sum()
    total_row = pd.DataFrame({args[1]: ['Total'], args[2]: [total_net]})
    return pd.concat([args[0], total_row], ignore_index=True)





def format_rupees(number):
    try:
        return format_decimal(number, locale='en_IN')
    except:
        return number

# def format_currency_old(number, number_type):
#     assert number_type in ['currency', 'decimal'], "Invalid number type passed"
#
#     if number_type == 'currency':
#         formatted_currency = format_currency(number, 'INR', locale='en_IN')
#     elif number_type == 'decimal':
#         formatted_decimal = format_decimal(number, locale='en_IN')