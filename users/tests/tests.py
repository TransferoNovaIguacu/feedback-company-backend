import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User

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

    #Resulta em um erro por não aceitar um acdess token, e sim um refresh token
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

    #     # Tenta acessar uma rota protegida após logout (dependendo da configuração do backend)
    #     protected_response = self.client.get(self.user_detail_url)

    #     # Verifica se o token não funciona mais (se for blacklist, depende de configuração)
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

        assert logout_response.status_code in [200, 204]  # Dependendo da configuração

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