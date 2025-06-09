# missions/serializers.py
from rest_framework import serializers
from .models import Mission, Feedback
from plans.serializers import ContractedPlanSerializer

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
        read_only_fields = ('mission', 'user', 'company', 'created_at')

class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = '__all__'
        read_only_fields = ('status', 'created_at', 'updated_at')

class SubmitFeedbackSerializer(serializers.Serializer):
    feedback_text = serializers.CharField(max_length=1000)

class AcceptMissionSerializer(serializers.Serializer):
    mission_id = serializers.IntegerField()