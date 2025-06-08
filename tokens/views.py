from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ObjectDoesNotExist

from tokens.models import TokenWallet
from tokens.serializers import AmountSerializer


class TokenBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, created = TokenWallet.objects.get_or_create(user=request.user)
        return Response({'balance': wallet.balance}, status=status.HTTP_200_OK)


@extend_schema(
    request=AmountSerializer,
    responses={200: AmountSerializer},
    description="Adiciona tokens à carteira do usuário."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_tokens(request):
    serializer = AmountSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    amount = serializer.validated_data['amount']
    wallet, _ = TokenWallet.objects.get_or_create(user=request.user)
    wallet.add_tokens(amount)
    return Response({
        'message': f'{amount} tokens adicionados com sucesso.',
        'balance': wallet.balance
    }, status=status.HTTP_200_OK)


@extend_schema(
    request=AmountSerializer,
    responses={200: AmountSerializer},
    description="Remove tokens da carteira do usuário."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_tokens(request):
    serializer = AmountSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    amount = serializer.validated_data['amount']
    wallet, _ = TokenWallet.objects.get_or_create(user=request.user)

    if wallet.remove_tokens(amount):
        return Response({
            'message': f'{amount} tokens removidos com sucesso.',
            'balance': wallet.balance
        }, status=status.HTTP_200_OK)

    return Response({'error': 'Saldo insuficiente para remover tokens.'}, status=status.HTTP_400_BAD_REQUEST)
