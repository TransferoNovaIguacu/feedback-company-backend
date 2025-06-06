import pytest
from django.core.exceptions import ValidationError
from companies.models import Company
from users.models import User

@pytest.mark.django_db
def test_create_company_valid():
    user = User.objects.create_user(email="empresa@teste.com", password="senha123")

    company = Company.objects.create(
        user=user,
        commercial_name="Minha Empresa Ltda",
        legal_name="Minha Empresa Ltda",
        cnpj="12345678000195",
        website="https://www.minhaempresa.com.br",
        logo_url="https://www.minhaempresa.com.br/logo.png",
        verified=True,
        tokens_balance=100.0,
        corporate_tax_id="123456789012",
    )

    assert company.id is not None
    assert company.commercial_name == "Minha Empresa Ltda"

@pytest.mark.django_db
def test_create_company_invalid_cnpj():
    user = User.objects.create_user(email="empresa@teste.com", password="senha123")

    with pytest.raises(ValidationError):
        company = Company(
            user=user,
            commercial_name="Empresa Invalida",
            legal_name="Empresa Invalida",
            cnpj="12345678",
            website="https://www.empresainvalida.com.br",
            logo_url="https://www.empresainvalida.com.br/logo.png",
            verified=False,
            tokens_balance=0.0,
            corporate_tax_id="9876543210",
        )
        company.full_clean()

@pytest.mark.django_db
def test_create_company_without_mandatory_fields():
    user = User.objects.create_user(email="empresa@teste.com", password="senha123")

    company = Company.objects.create(
        user=user,
        commercial_name="Empresa Sem Razão Social",
        legal_name="",
        cnpj="12345678000195",
        website="",
        logo_url="",
        verified=False,
        tokens_balance=50.0,
        corporate_tax_id="1234567890",
    )

    assert company.legal_name == ""

@pytest.mark.django_db
def test_create_company_default_values():
    user = User.objects.create_user(email="empresa@teste.com", password="senha123")

    company = Company.objects.create(
        user=user,
        commercial_name="Empresa Default",
        legal_name="Empresa Default",
        cnpj="98765432000199",
    )

    assert company.tokens_balance == 0
    assert company.verified is False
    assert company.corporate_tax_id == ""

@pytest.mark.django_db
def test_create_company_invalid_cnpj_format():
    user = User.objects.create_user(email="empresa@teste.com", password="senha123")

    with pytest.raises(ValidationError):
        company = Company(
            user=user,
            commercial_name="CNPJ Inválido",
            legal_name="CNPJ Inválido",
            cnpj="12.345.678/0001-99",
            website="https://www.cnpjinválido.com",
            logo_url="https://www.cnpjinválido.com/logo.png",
            verified=False,
            tokens_balance=0.0,
            corporate_tax_id="000000000000",
        )
        company.full_clean()

@pytest.mark.django_db
def test_company_str_method():
    user = User.objects.create_user(email="empresa@teste.com", password="senha123")

    company = Company.objects.create(
        user=user,
        commercial_name="Empresa de Teste",
        legal_name="Empresa de Teste Ltda",
        cnpj="12345678000195",
        website="https://www.empresa.com",
        logo_url="https://www.empresa.com/logo.png",
        verified=False,
        tokens_balance=100.0,
        corporate_tax_id="9876543210",
    )

    assert str(company) == "Empresa de Teste (Company)"

@pytest.mark.django_db
def test_create_company_with_optional_fields():
    user = User.objects.create_user(email="empresa@teste.com", password="senha123")

    company = Company.objects.create(
        user=user,
        commercial_name="Empresa com Campos Opcionais",
        legal_name="Empresa com Campos Opcionais Ltda",
        cnpj="98765432000199",
        website="https://www.empresaopcional.com",
        logo_url="https://www.empresaopcional.com/logo.png",
        verified=True,
        tokens_balance=250.0,
        corporate_tax_id="1234567890",
    )

    assert company.website == "https://www.empresaopcional.com"
    assert company.logo_url == "https://www.empresaopcional.com/logo.png"
    assert company.business_area == ""
    assert company.corporate_tax_id == "1234567890"