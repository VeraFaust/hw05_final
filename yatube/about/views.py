from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Страница с информацией об авторе."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Страница с информацией о технологиях."""
    template_name = 'about/tech.html'
