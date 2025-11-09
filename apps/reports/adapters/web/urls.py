from django.urls import path
from . import views  # Asegúrate de importar views

app_name = 'reports'

urlpatterns = [
    path('informe/', views.informe, name='informe'),
]