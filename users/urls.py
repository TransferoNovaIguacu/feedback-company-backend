from django.urls import path
from .views import TestView

urlpatterns = [
    path('teste/', TestView.as_view()),
]