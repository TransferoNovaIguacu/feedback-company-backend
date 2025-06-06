from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Mission, Feedback, QuizAnswer
from .serializers import MissionSerializer, FeedbackSerializer, QuizAnswerSerializer


class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    permission_classes = [IsAuthenticated]


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]


class QuizAnswerViewSet(viewsets.ModelViewSet):
    queryset = QuizAnswer.objects.all()
    serializer_class = QuizAnswerSerializer
    permission_classes = [IsAuthenticated]