from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InitialView, CompanyViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)

urlpatterns = [
    path("", InitialView.as_view()),
    path("", include(router.urls)),
]
