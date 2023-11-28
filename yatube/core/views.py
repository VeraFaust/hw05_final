from django.shortcuts import render


def page_not_found(request, exception):
    """Ошибка 404: страница не найдена."""
    return render(
        request,
        'core/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    """Ошибка 500: сбой на сервере."""
    return render(
        request,
        'core/500.html',
        status=500
    )


def permission_denied(request, exception):
    """Ошибка 403: отклонение запроса."""
    return render(
        request,
        'core/403.html',
        status=403
    )


def csrf_failure(request, reason=''):
    """Ошибка 403: ошибка проверки CSRF."""
    return render(
        request,
        'core/403csrf.html'
    )
