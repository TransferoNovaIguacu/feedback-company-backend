from django.urls import path
from tokens import views as token_views

urlpatterns = [
    path('wallet/balance/', token_views.TokenBalanceView.as_view(), name='token_balance'),
    path('wallet/add/', token_views.add_tokens, name='add_tokens'),
    path('wallet/remove/', token_views.remove_tokens, name='remove_tokens'),
]