import json
from unittest.mock import patch
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from companies.models import Company

@pytest.mark.django_db
class TestCompanyRegistration:

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('company_register')

    def test_register_company_success(self):
        data = {
            "email": "empresa1@teste.com",
            "password1": "SenhaForte123",
            "password2": "SenhaForte123",
            "commercial_name": "Empresa Teste",
            "legal_name": "Empresa Teste LTDA",
            "business_area": "Tecnologia",
            "cnpj": "84480679000153"
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        print("\n✅ Sucesso:", response.status_code, response.json())
        assert response.status_code == 201
        assert Company.objects.filter(email="empresa1@teste.com").exists()

    def test_register_company_invalid_cnpj(self):
        data = {
            "email": "empresa2@teste.com",
            "password1": "SenhaForte123",
            "password2": "SenhaForte123",
            "commercial_name": "Empresa Inválida",
            "legal_name": "Empresa Inválida LTDA",
            "business_area": "Tecnologia",
            "cnpj": "00000000000000"
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        print("\n🚫 CNPJ inválido:", response.status_code, response.json())
        assert response.status_code == 400
        assert "cnpj" in response.json()

    def test_register_company_duplicate_email(self):
        Company.objects.create_user(
            email="empresa3@teste.com",
            password="SenhaForte123",
            commercial_name="Empresa 3",
            legal_name="Empresa 3 LTDA",
            cnpj="84480679000153",
            user_type="COMPANY"
        )
        data = {
            "email": "empresa3@teste.com",
            "password1": "SenhaForte123",
            "password2": "SenhaForte123",
            "commercial_name": "Empresa Duplicada",
            "legal_name": "Empresa Duplicada LTDA",
            "business_area": "TI",
            "cnpj": "84480679000153"
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        print("\n🚫 Email duplicado:", response.status_code, response.json())
        assert response.status_code == 400
        assert "email" in response.json()

    def test_register_company_duplicate_cnpj(self):
        Company.objects.create_user(
            email="empresa4@teste.com",
            password="SenhaForte123",
            commercial_name="Empresa 4",
            legal_name="Empresa 4 LTDA",
            cnpj="84480679000153",
            user_type="COMPANY"
        )
        data = {
            "email": "empresa5@teste.com",
            "password1": "SenhaForte123",
            "password2": "SenhaForte123",
            "commercial_name": "Empresa Duplicada CNPJ",
            "legal_name": "Empresa Duplicada LTDA",
            "business_area": "TI",
            "cnpj": "84480679000153"
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        print("\n🚫 CNPJ duplicado:", response.status_code, response.json())
        assert response.status_code == 400
        assert "cnpj" in response.json()

    def test_register_company_missing_fields(self):
        data = {
            "email": "empresa6@teste.com",
            "password1": "SenhaForte123",
            "password2": "SenhaForte123",
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        print("\n🚫 Campos ausentes:", response.status_code, response.json())
        assert response.status_code == 400
        assert "commercial_name" in response.json()
        assert "legal_name" in response.json()
        assert "cnpj" in response.json()

    def test_register_company_passwords_dont_match(self):
        data = {
            "email": "empresa7@teste.com",
            "password1": "SenhaForte123",
            "password2": "SenhaErrada123",
            "commercial_name": "Empresa",
            "legal_name": "Empresa LTDA",
            "cnpj": "84480679000153"
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        print("\n🚫 Senhas diferentes:", response.status_code, response.json())
        assert response.status_code == 400
        assert "non_field_errors" in response.json()

    def test_register_company_internal_server_error(self):
        with patch('companies.serializers.Company.objects.create_user', side_effect=Exception("Erro interno")):
            data = {
                "email": "empresa8@teste.com",
                "password1": "SenhaForte123",
                "password2": "SenhaForte123",
                "commercial_name": "Empresa",
                "legal_name": "Empresa LTDA",
                "cnpj": "84480679000153"
            }
            response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
            print("\n🔥 Erro interno forçado:", response.status_code, response.json())
            assert response.status_code in [400, 500]
            assert "detail" in response.json()
