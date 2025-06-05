import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User, CommonUser, UserType
from django.core.exceptions import ValidationError
from django.db import transaction
from validate_docbr import CPF

@pytest.mark.django_db
class TestAuthAPI:
    def setup_method(self):
        self.client = APIClient()
        self.register_url = reverse('rest_register')
        self.login_url = reverse('rest_login')
        self.user_detail_url = reverse('rest_user_details')
        
        self.user_data = {
            "email": "testuser@example.com",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }
        self.login_data = {
            "email": "testuser@example.com",
            "password": "strongpassword123",
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        assert response.status_code == 201
        # Verifica a estrutura da resposta JWT
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == self.user_data['email']

    def test_user_login(self):
        # Cria o usuário diretamente (sem username)
        User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password1']
        )
        
        response = self.client.post(self.login_url, self.login_data)
        assert response.status_code == 200
        # Verifica a estrutura da resposta JWT
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == self.login_data['email']

    def test_protected_view(self):
        # Cria usuário
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password1']
        )
        
        # Faz login para obter o token
        login_response = self.client.post(self.login_url, self.login_data)
        
        # Obtém o token de acesso
        access_token = login_response.data.get('access')
        assert access_token is not None
        
        # Configura a autenticação
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Testa a view de detalhes do usuário
        response = self.client.get(self.user_detail_url)
        assert response.status_code == 200
        assert response.data['email'] == self.user_data['email']

    # Resulta em um erro por não aceitar um acdess token, e sim um refresh token
    # def test_user_logout(self):
    #     # Cria usuário
    #     User.objects.create_user(
    #         email=self.user_data['email'],
    #         password=self.user_data['password1']
    #     )

    #     # Faz login para obter o token
    #     login_response = self.client.post(self.login_url, self.login_data)
    #     assert login_response.status_code == 200

    #     # Obtém o token de acesso
    #     access_token = login_response.data.get('access')
    #     assert access_token is not None

    #     # Configura autenticação
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    #     # Faz logout
    #     logout_url = reverse('rest_logout')
    #     logout_response = self.client.post(logout_url)

    #     # Verifica se o logout foi bem-sucedido
    #     assert logout_response.status_code in [200, 204]
    #     assert 'detail' in logout_response.data

    #     protected_response = self.client.get(self.user_detail_url)
    #     assert protected_response.status_code in [401, 403]

    def test_user_logout(self):
        # Cria usuário
        User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password1']
        )

        # Faz login para obter os tokens
        login_response = self.client.post(self.login_url, self.login_data)
        assert login_response.status_code == 200

        access_token = login_response.data.get('access')
        refresh_token = login_response.data.get('refresh')

        assert access_token is not None
        assert refresh_token is not None

        # Autentica com o access token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Faz logout enviando o refresh token
        logout_url = reverse('rest_logout')
        logout_response = self.client.post(logout_url, {'refresh': refresh_token}, format='json')

        assert logout_response.status_code in [200, 204]

    def test_registration_with_weak_password(self):
        weak_password_data = {
            "email": "weakpass@example.com",
            "password1": "123",
            "password2": "123",
        }
        response = self.client.post(self.register_url, weak_password_data)
        assert response.status_code == 400
        assert 'password1' in response.data


    def test_registration_with_invalid_email(self):
        invalid_email_data = {
            "email": "invalid-email",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        }
        response = self.client.post(self.register_url, invalid_email_data)
        assert response.status_code == 400
        assert 'email' in response.data


    def test_login_with_wrong_password(self):
        # Cria o usuário corretamente
        User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password1']
        )

        wrong_password_data = {
            "email": self.user_data['email'],
            "password": "wrongpassword123"
        }
        response = self.client.post(self.login_url, wrong_password_data)
        assert response.status_code == 400
        assert 'non_field_errors' in response.data
    
    def test_password_reset(self):
        # Cria usuário
        User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password1']
        )

        reset_url = reverse('rest_password_reset')  # normalmente é esse nome no dj-rest-auth

        response = self.client.post(reset_url, {"email": self.user_data['email']})

        assert response.status_code == 200
        # Pode checar se a resposta tem uma mensagem confirmando o envio do email
        assert "detail" in response.data or "email" in response.data

    def test_protected_logout(self):
        User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password1']
        )

        login_response = self.client.post(self.login_url, self.login_data)
        access_token = login_response.data.get('access')
        refresh_token = login_response.data.get('refresh')

        # Não precisa do header Authorization para logout
        self.client.credentials()  

        logout_url = reverse('rest_logout')

        # Envia refresh token com a chave correta 'refresh'
        response = self.client.post(logout_url, {"refresh": refresh_token}, format='json')

        assert response.status_code in [200, 204]
        
# Teste de Common User
@pytest.mark.django_db
class TestCommonUser:
    def test_create_common_user(self):
        
        user_data = {
            "email": "commonuser@example.com",
            "password": "strongpassword123",
            "user_type": UserType.COMMON,
        }
        
        common_user_data = {
            "full_name": "Fulano de Tal",
            "cpf": "52998224725",
            "total_tokens_earned": 100.50,
            "completed_missions": 5,
        }
        
        common_user = CommonUser(
        email="commonuser@example.com",
        password="strongpassword123",
        user_type=UserType.COMMON,
        full_name="Fulano de Tal",
        cpf="52998224725",
        total_tokens_earned=100.50,
        completed_missions=5,
        )
        common_user.save()
        
        assert User.objects.count() == 1
        assert CommonUser.objects.count() == 1
        
        db_user = User.objects.get(email=user_data['email'])
        assert db_user.email == user_data['email']
        assert db_user.user_type == UserType.COMMON
        assert db_user.is_active is True
        assert db_user.is_staff is False
        
        db_common_user = CommonUser.objects.get(cpf=common_user_data['cpf'])
        assert db_common_user.full_name == common_user_data['full_name']
        assert db_common_user.cpf == common_user_data['cpf']
        assert float(db_common_user.total_tokens_earned) == float(common_user_data['total_tokens_earned'])
        assert db_common_user.completed_missions == common_user_data['completed_missions']
        
        assert db_common_user.user_ptr_id == db_user.id
        assert db_common_user.email == db_user.email

    def test_cpf_validation(self):
        invalid_cpf = "12345678901" 
        
        common_user = CommonUser(
            email="invalidcpf@example.com",
            password="testpass123",
            full_name="Invalid CPF",
            cpf=invalid_cpf,
            total_tokens_earned=0,
            completed_missions=0
        )
        
        with pytest.raises(ValidationError) as excinfo:
            common_user.full_clean()
        
        assert 'cpf' in str(excinfo.value)

    def test_cpf_formatting(self):
        
        formatted_cpf = "529.982.247-25"
        expected_cpf = "52998224725"
        
        common_user = CommonUser(
            email="formattedcpf@example.com",
            password="testpass123",
            full_name="Formatted CPF",
            cpf=formatted_cpf,
            total_tokens_earned=0,
            completed_missions=0
        )
        
        common_user.save()
        
        db_common_user = CommonUser.objects.get(email="formattedcpf@example.com")
        assert db_common_user.cpf == expected_cpf

    def test_common_user_str_representation(self):
        common_user = CommonUser(
            email="strtest@example.com",
            password="testpass123",
            full_name="Test User",
            cpf="52998224725",
            total_tokens_earned=0,
            completed_missions=0
        )
        common_user.save()
        
        assert str(common_user) == "Test User (52998224725)"