from django.test import TestCase
from django.contrib.auth import get_user_model
from companies.models import Company
from plans.models import Plan, ContractedPlan
from missions.models import Mission, Feedback
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from tokens.models import TokenWallet
from users.models import CommonUser

User = get_user_model()

class ErrorCasesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Criar usuário comum   
        self.common_user = CommonUser.objects.create(
        email="teste3@teste.com",
        password="testesenha@123",
        full_name="Test User",
        cpf="11858919789"
        )
        
        self.wallet = TokenWallet.objects.create(
        user=self.common_user,
        balance=0
        )
        
        # Criar outro usuário 
        self.other_user = CommonUser.objects.create(
        email="other@test.com",
        password="testpass123",
        full_name="Other User",
        cpf="98765432109"
        )
        
        self.wallet = TokenWallet.objects.create(
        user=self.other_user,
        balance=0
        )
        
        # Criar empresa   
        self.company = Company.objects.create(
        email="company@test.com",
        password="testpass123",
        commercial_name="Test Company",
        legal_name="Test Company LTDA",
        cnpj="99770423000158",
        website="https://www.minhaempresa.com.br",
        logo_url="https://www.minhaempresa.com.br/logo.png",
        verified=True,
        tokens_balance=100.0,
        corporate_tax_id="123456789012",
        )
        
        # Criar plano
        self.plan = Plan.objects.create(
            name='Basic Plan',
            description='Test plan',
            token_value=100,
            feedbacks_available=5,
            quests_available=3,
            reward_percentage=0.6
        )
        
        # Criar plano contratado
        self.contracted_plan = ContractedPlan.objects.create(
            company=self.company,
            plan=self.plan,
            expiration_date=timezone.now() + timedelta(days=30)
        )
        
        # Criar missão
        self.mission = Mission.objects.create(
            contracted_plan=self.contracted_plan,
            mission_type='FEEDBACK',
            title='Test Mission',
            description='Test Description',
            url='http://test.com',
            status='PENDING'
        )
        
        # Autenticar usuário comum
        self.client.force_authenticate(user=self.common_user)

    def test_accept_mission_twice(self):
        # Primeiro aceite deve funcionar
        url = reverse('mission-accept', kwargs={'pk': self.mission.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Tentar aceitar novamente deve falhar
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_feedback_to_others_mission(self):
        # Outro usuário aceita a missão
        self.mission.activate(self.other_user)
        
        # Usuário atual tenta enviar feedback
        url = reverse('mission-submit-feedback', kwargs={'pk': self.mission.id})
        data = {'feedback_text': 'Test feedback'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_empty_feedback(self):
        # Aceitar a missão primeiro
        self.mission.activate(self.common_user)
        
        url = reverse('mission-submit-feedback', kwargs={'pk': self.mission.id})
        data = {'feedback_text': ''}  # Feedback vazio
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)