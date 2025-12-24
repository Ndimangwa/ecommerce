from django.urls import path
from . import views

app_name='church'

urlpatterns = [
    path('', views.load_by_name, name='load_by_name'),
    path('load_by_position', views.load_by_position, name='load_by_position'),
]