from django.utils import timezone
from rest_framework import serializers
from .models import Plan, ContractedPlan
from drf_spectacular.utils import extend_schema_field

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class ContractedPlanSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = ContractedPlan
        fields = '__all__'
        read_only_fields = ('purchase_date', 'remaining_feedbacks', 'remaining_quests')

    @extend_schema_field(bool)
    def get_is_expired(self, obj) -> bool:
        return obj.expiration_date < timezone.now()