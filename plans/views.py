from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Plan, ContractedPlan
from .serializers import PlanSerializer, ContractedPlanSerializer
from companies.models import Company
from django.utils import timezone
from datetime import timedelta

class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Exemplo: filtrar apenas planos ativos
        return Plan.objects.filter(is_active=True)

class ContractedPlanViewSet(viewsets.ModelViewSet):
    serializer_class = ContractedPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        if self.request.user.is_staff:
            return ContractedPlan.objects.all()
        return ContractedPlan.objects.filter(company__user=self.request.user)

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):

        plan = Plan.objects.get(pk=pk)
        company = Company.objects.get(user=request.user)
        
        expiration_date = timezone.now() + timedelta(days=30)
        
        contracted_plan = ContractedPlan.objects.create(
            company=company,
            plan=plan,
            remaining_feedbacks=plan.feedbacks_available,
            remaining_quests=plan.quests_available,
            expiration_date=expiration_date
        )
        
        serializer = self.get_serializer(contracted_plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        formatted_data = []
        for plan in serializer.data:
            formatted_data.append({
                "plano": plan["name"],
                "preco_do_plano": str(plan["token_value"]),
                "descricao": plan["description"],
                "feedbacks_disponiveis": plan["feedbacks_available"],
                "missoes_disponiveis": plan["quests_available"],
                "porcentagem_recompensa": str(plan["reward_percentage"]),
            })
        
        return Response(formatted_data)