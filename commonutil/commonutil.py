import random
import string
from datetime import datetime
import os
from babel.numbers import format_decimal

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
