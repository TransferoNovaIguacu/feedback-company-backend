from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class UserType(models.TextChoices):
    COMMON = "COMMON", "Common User"
    COMPANY = "COMPANY", "Company"
    STAFF = "STAFF", "Staff"
    ANALYST = "ANALYST", "Analyst"
    ADMIN = "ADMIN", "Admin"

class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
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

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email