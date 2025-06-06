import datetime
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator
from companies.models import Company

class Contracted_Plan(models.Model):
    PLAN_TYPES = [
        ('BASIC', 'Basic'),
        ('PRO', 'Profissional'),
        ('ENTERPRISE', 'Company'),
        ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="plans")
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, verbose_name="Tipo de Plano")
    start_date = models.DateField(verbose_name="Data de Início")
    end_date = models.DateField(verbose_name="Data de Término")
    is_active = models.BooleanField(default=True, verbose_name="Ativo?")
    
    class Meta:
        verbose_name = "Contracted plan"
        verbose_name_plural = "Contracted plans"
    
    def __str__(self):
        return f"{self.company.commercial_name} - {self.get_plan_type_display()}"


# Enums/Choices (podem ficar no topo ou próximos aos modelos que os usam)
class MissionType(models.TextChoices):
    FEEDBACK = 'FB', 'Seach'
    QUIZ = 'QZ', 'questionnaire'



# Modelo Mission (depende dos modelos acima)
class Mission(models.Model):
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        related_name="missions",
        verbose_name="Company"
    )
    contracted_plan = models.ForeignKey(
        Contracted_Plan,
        on_delete=models.PROTECT,
        related_name="missions",
        verbose_name="Contracted plan"
    )
    mission_type = models.CharField(
        max_length=2,
        choices=MissionType.choices,
        verbose_name="Mission Type"
    )
    title = models.CharField(max_length=100, verbose_name="Title")
    description = models.TextField(verbose_name="Description")
    tokens_reward = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Tokens Reward"
    )
    is_active = models.BooleanField(default=True, verbose_name="Active?")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Creation Date")
    expiration_date = models.DateTimeField(verbose_name="Expiration Date")

    estimated_time = models.PositiveIntegerField(
        help_text="Estimated duration in minutes",
        verbose_name="Estimated Time (min)"
    )

    class Meta:
        verbose_name = "Mission"
        verbose_name_plural = "Missions"
        ordering = ['-creation_date']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):

        self.is_active = self.expiration_date > timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        return not self.is_active


# Enums para Feedback
class Rating(models.TextChoices):
    BAD = 'bad', 'Bad'
    GOOD = 'good', 'Good'
    EXCELLENT = 'excellent', 'Excellent'


class ApprovalStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'


# Modelo Feedback (depende de Mission e Company)
class Feedback(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="feedbacks",
        verbose_name="Company"
    )
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name="feedbacks",
        verbose_name="Mission"
    )
    content = models.TextField(verbose_name="Feedback Content")
    rating = models.CharField(
        max_length=10,
        choices=Rating.choices,
        verbose_name="Feedback"
    )
    tokens_rewarded = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Rewarded Tokens"
    )
    submission_date = models.DateTimeField(auto_now_add=True, verbose_name="Submission date")
    status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
        verbose_name="Approving Status"
    )

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
        ordering = ['-submission_date']
    
    def __str__(self):
        return f"Feedback para {self.mission.title} - {self.get_status_display()}"


class QuizAnswer(models.Model):
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="quiz_answers",
        verbose_name="Company"
    )
    mission = models.ForeignKey(
        "Mission",
        on_delete=models.CASCADE,
        related_name="quiz_answers",
        verbose_name="Mission"
    )
    answers = models.JSONField(
        verbose_name="Answers",
        help_text="Quiz Answers "
    )
    completion_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Completion Date"
    )
    tokens_rewarded = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Tokens Rewarded",
        validators=[MinValueValidator(0)]
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Verified?"
    )

    class Meta:
        verbose_name = "Quiz Answer"
        verbose_name_plural = "Quiz Answers"
        ordering = ['-completion_date']  # Ordena do mais recente para o mais antigo
        indexes = [
            models.Index(fields=['mission', 'company']),  # Melhora performance de consultas
            models.Index(fields=['completion_date']),
        ]

    def __str__(self):
        return f"Resposta para {self.mission.title} ({self.company.name})"