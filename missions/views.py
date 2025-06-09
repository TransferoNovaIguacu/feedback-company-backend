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
    
    def get_queryset(self):
        user = self.request.user
        return Mission.objects.filter(status="PENDING")

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