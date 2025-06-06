from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from tokens.models import TokenWallet

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def token_balance(request):
    wallet, created = TokenWallet.objects.get_or_create(user=request.user)
    return Response({'balance': wallet.balance})