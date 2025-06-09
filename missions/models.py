# missions/models.py
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from companies.models import Company
from plans.models import ContractedPlan
from django.utils import timezone

from tokens.models import TokenWallet
from users.models import CommonUser

User = get_user_model()

class Mission(models.Model):
    MISSION_TYPES = (
        ('FEEDBACK', 'Feedback'),
        ('QUIZ', 'Quiz'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('EXPIRED', 'Expired'),
    )
    
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='missions')
    contracted_plan = models.ForeignKey(ContractedPlan, on_delete=models.CASCADE, related_name='missions')
    mission_type = models.CharField(max_length=10, choices=MISSION_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='missions_assigned')
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def activate(self, user):
        if self.status == 'PENDING':
            self.status = 'ACTIVE'
            self.assigned_to = user
            self.save()
            return True
        return False
    
    def complete(self, feedback_text):
        if self.status == 'ACTIVE':
            # Cria o feedback
            feedback = Feedback.objects.create(
                mission=self,
                user=self.assigned_to,
                feedback_text=feedback_text,
                company=self.contracted_plan.company
            )
            
            # Atualiza o plano contratado
            if self.mission_type == 'FEEDBACK':
                self.contracted_plan.decrement_feedback()
            
            # Muda status da missão
            self.status = 'COMPLETED'
            self.save()
            
            # Distribui recompensas (implementar lógica de tokens)
            self.distribute_rewards()
            
            return feedback
        return None
    
    def distribute_rewards(self):
        plan = self.contracted_plan.plan
        reward_amount = Decimal(plan.token_value)
        
        wallet, created = TokenWallet.objects.get_or_create(
        user=self.assigned_to,
        defaults={'balance': Decimal('0.0')}
        )
    
        # Adiciona os tokens ao saldo local
        wallet.balance += reward_amount
        wallet.save()
        
        # Poderia também registrar a transação em um modelo de Transaction se necessário

class Feedback(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_feedbacks') 
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_feedbacks') 
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.user.username} for {self.company.commercial_name}"