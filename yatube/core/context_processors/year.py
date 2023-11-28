import datetime


def year(request):
    """Переменная с текущим годом."""
    year = datetime.datetime.now().year
    return {
        'year': year,
    }
