# missions/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Mission, Feedback
from .serializers import MissionSerializer, FeedbackSerializer, SubmitFeedbackSerializer
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

class MissionViewSet(viewsets.ModelViewSet):
    serializer_class = MissionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Mission.objects.all()
    
    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, 'company'):
            return Response({'error': 'Apenas empresas podem criar missões.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(company=request.user.company)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        return Mission.objects.filter(status="PENDING")
    
    @extend_schema(
        responses={200: MissionSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='company-missions')
    def company_missions(self, request):
        if not hasattr(request.user, 'company'):
            return Response({'error': 'Apenas empresas podem acessar essa rota.'}, status=status.HTTP_403_FORBIDDEN)
        
        status_param = request.query_params.get('status')
        queryset = Mission.objects.filter(company=request.user.company)
        if status_param:
            queryset = queryset.filter(status=status_param.upper())
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID da missão'
            )
        ]
    )
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        mission = self.get_object()
        if mission.status == 'PENDING':
            if mission.activate(request.user):
                return Response({'status': 'Missão aceita'}, status=status.HTTP_200_OK)
            return Response({'error': 'Missão não pode ser ativada'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Missão não disponível'}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=SubmitFeedbackSerializer,
        responses={200: MissionSerializer}
    )
    @action(detail=True, methods=['post'])
    def submit_feedback(self, request, pk=None):
        mission = self.get_object()
        
        if mission.status != 'ACTIVE' or mission.assigned_to != request.user:
            return Response(
                {'error': 'Essa missão foi designada.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = SubmitFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            feedback_text = serializer.validated_data['feedback_text']
            mission.complete(feedback_text)
            return Response(MissionSerializer(mission).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FeedbackViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    queryset = Feedback.objects.none()  # Placeholder queryset
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID do feedback'
            )
        ]
    )
    def get_queryset(self):
        if hasattr(self.request.user, 'company'):
            return Feedback.objects.filter(company=self.request.user.company)
        return Feedback.objects.filter(user=self.request.user)