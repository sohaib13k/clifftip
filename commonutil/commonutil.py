import random
import string
from datetime import datetime, timedelta
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
