from django.urls import path
from . import views


app_name = 'about'

urlpatterns = [
    # Информация об авторе
    path('author/', views.AboutAuthorView.as_view(), name='author'),
    # Информация о технологиях
    path('tech/', views.AboutTechView.as_view(), name='tech'),
]
