from django.db import models
from django.contrib.auth.models import AbstractUser


class UserType(models.TextChoices):
    COMMON = "COMMON", "Common User"
    COMPANY = "COMPANY", "Company"
    STAFF = "STAFF", "Staff"
    ANALYST = "ANALYST", "Analyst"
    ADMIN = "ADMIN", "Admin"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.COMMON,
        help_text="Tipo de usuário (define comportamento e permissões)."
    )

    wallet_address = models.CharField(
        max_length=42,
        blank=True,
        null=True,
        help_text="Endereço da carteira blockchain do usuário."
    )

    blocked_tokens = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Tokens bloqueados temporariamente (ex: em análise de saque)."
    )

    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class CommonUser(User):
    full_name = models.CharField(
        max_length=255,
        help_text="Nome completo do usuário."
    )

    cpf = models.CharField(
        max_length=11,
        unique=True,
        help_text="CPF do usuário (apenas números)."
    )

    total_tokens_earned = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        help_text="Total de tokens ganhos pelo usuário desde o cadastro."
    )

    tokens_balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        help_text="Saldo de tokens disponíveis para saque (simulado off-chain)."
    )

    completed_missions = models.PositiveIntegerField(
        default=0,
        help_text="Quantidade de missões concluídas pelo usuário."
    )

    withdrawal_minimum = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        help_text="Valor mínimo para saque."
    )

    def __str__(self):
        return f"{self.full_name} (CommonUser)"


class Company(User):
    commercial_name = models.CharField(
        max_length=255,
        help_text="Nome fantasia da empresa."
    )

    cnpj = models.CharField(
        max_length=14,
        unique=True,
        help_text="CNPJ da empresa (apenas números)."
    )

    website = models.URLField(
        max_length=200,
        blank=True,
        help_text="URL do site oficial da empresa."
    )

    logo_url = models.URLField(
        blank=True,
        help_text="URL da logo da empresa."
    )

    verified = models.BooleanField(
        default=False,
        help_text="Indica se a empresa foi verificada pela plataforma."
    )

    tokens_balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        help_text="Saldo de tokens disponível para ações internas da empresa (off-chain)."
    )

    corporate_tax_id = models.CharField(
        max_length=20,
        blank=True,
        help_text="Inscrição estadual, municipal ou outro identificador fiscal."
    )

    def __str__(self):
        return f"{self.commercial_name} (Company)"
