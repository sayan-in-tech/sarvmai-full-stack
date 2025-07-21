from django.urls import path
from . import views

app_name = 'boarding'

urlpatterns = [
    path('', views.upload_csv, name='upload'),
    path('result/', views.result, name='result'),
    path('download/', views.download_csv, name='download'),
] 