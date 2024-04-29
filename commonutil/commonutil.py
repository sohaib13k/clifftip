import uuid
from datetime import datetime
import os


def uploaded_excel(f, location):
    """
    save excel file at specified location. Directory will be created recursivly if not exists

    :param location: location where write need to be done
    """
    if not os.path.exists(location):
        print(">>>>>>>>>>>>>>", location)
        os.makedirs(location, exist_ok=True)

    with open(location / f.name, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def get_unique_filename():
    today_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_suffix = uuid.uuid4()
    return f"{today_str}_{unique_suffix}"
