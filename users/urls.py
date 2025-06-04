from django.urls import include, path
from .views import TestView

urlpatterns = [
    path('teste/', TestView.as_view()),
]