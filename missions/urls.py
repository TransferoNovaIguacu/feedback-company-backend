from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MissionViewSet, FeedbackViewSet, QuizAnswerViewSet

router = DefaultRouter()
router.register(r'missions', MissionViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'quiz-answers', QuizAnswerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
