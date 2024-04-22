import pandas as pd

def append_total(*args):
    """
    Returns data_frame with a row appended with label 'Total' showing the sum of second column
    """
    total_net = args[0][args[2]].sum()
    total_row = pd.DataFrame({args[1]: ['Total'], args[2]: [total_net]})
    return pd.concat([args[0], total_row], ignore_index=True)


