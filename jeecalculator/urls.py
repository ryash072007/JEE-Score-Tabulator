from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_and_process, name='upload_and_process'),
    path('results/', views.results, name='results'),
]