from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenVerifyView
from tokens.views import token_balance

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/plans/', include('plans.urls')),
    path('api/balance/', token_balance, name='token-balance'),
    path('api/missions/', include('missions.urls')),
]