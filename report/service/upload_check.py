from django.http import HttpResponse


def routing_report(df):
    if "Lock/Unlock" not in df.columns:
        return HttpResponse(
            'Uploaded report doesn\'t contain "Lock/Unlock" column. Kindly upload the right report',
            status=404,
        )


def bom_report(df):
    if "Lock/Unlock" not in df.columns:
        return HttpResponse(
            'Uploaded report doesn\'t contain "Lock/Unlock" column. Kindly upload the right report',
            status=404,
        )
