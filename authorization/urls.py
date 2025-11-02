from django.urls import path
from . import views

app_name="authorization"

urlpatterns = [
    path('not_allowed/', views.not_allowed, name='not_allowed'),
]
