# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Company(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='company'
    )
    name = models.CharField(max_length=100, unique=True)
    ms = models.CharField(max_length=50, unique=True)  # CNPJ ou identificador único
    address = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['-created_at']

    @property
    def active_plan(self):
        """Retorna o plano ativo da empresa, se existir"""
        return self.contracted_plans.filter(
            is_active=True,
            expiration_date__gte=timezone.now()
        ).first()

    @property
    def remaining_feedbacks(self):
        """Quantidade de feedbacks restantes no plano ativo"""
        plan = self.active_plan
        return plan.remaining_feedbacks if plan else 0

    @property
    def remaining_quests(self):
        """Quantidade de quizzes restantes no plano ativo"""
        plan = self.active_plan
        return plan.remaining_quests if plan else 0