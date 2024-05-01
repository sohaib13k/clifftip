import pandas as pd


def append_total(*args):
    """
    Returns data_frame with a row appended with label 'Total' showing the sum of second column
    """
    total_net = args[0][args[2]].sum()
    total_row = pd.DataFrame({args[1]: ["Total"], args[2]: [total_net]})
    return pd.concat([args[0], total_row], ignore_index=True)


def add_percentage_column(df, total_col_name):
    total_sum = df[total_col_name].iloc[-1]  # Accessing the last element in the column
    if total_sum == 0:  # Avoid division by zero
        df["Percentage"] = 0
    else:
        # Calculate the percentage of each row relative to the total sum
        df["Percentage"] = (df[total_col_name] / total_sum * 100).round(2)
    return df
