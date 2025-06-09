# missions/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MissionViewSet, FeedbackViewSet
from users.models import CommonUser

router = DefaultRouter()
router.register(r'missions', MissionViewSet, basename='mission')
router.register(r'feedbacks', FeedbackViewSet, basename='feedback')

urlpatterns = [
    path('', include(router.urls)),
]