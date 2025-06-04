from django.urls import path, include
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('users/', include('users.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("companies/", include("companies.urls")),
    path("missions/", include("missions.urls")),
    path("feedbacks/", include("feedbacks.urls")),
    path("tokens/", include("tokens.urls")),
    path("reports/", include("reports.urls")),
    path("web3/", include("web3integration.urls")), 
]