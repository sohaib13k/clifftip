import os


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
