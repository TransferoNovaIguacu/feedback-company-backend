from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from companies.models import Company
from plans.models import Plan, ContractedPlan
from missions.models import Feedback, Mission
from django.utils import timezone
from datetime import timedelta

from tokens.models import TokenWallet
from users.models import CommonUser

User = get_user_model()

class MissionViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Criar usuário comum
        self.common_user = CommonUser.objects.create(
        email="teste3@teste.com",
        password="testesenha@123",
        full_name="Test User",
        cpf="11858919789",
    )
        
        # Criar empresa
        self.company = Company.objects.create(
        email="teste@teste.com",
        password="testesenha@123",
        commercial_name="Minha Empresa Ltda",
        legal_name="Minha Empresa Ltda",
        cnpj="99770423000158",
        website="https://www.minhaempresa.com.br",
        logo_url="https://www.minhaempresa.com.br/logo.png",
        verified=True,
        tokens_balance=100.0,
        corporate_tax_id="123456789012",
        )
        
        self.wallet = TokenWallet.objects.create(
        user=self.common_user,
        balance=0
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
        
        # Criar missões
        self.mission1 = Mission.objects.create(
            contracted_plan=self.contracted_plan,
            mission_type='FEEDBACK',
            title='Mission 1',
            description='Description 1',
            url='http://test.com/1',
            status='PENDING'
        )
        
        self.mission2 = Mission.objects.create(
            contracted_plan=self.contracted_plan,
            mission_type='FEEDBACK',
            title='Mission 2',
            description='Description 2',
            url='http://test.com/2',
            status='PENDING'
        )
        
        # Autenticar usuário comum
        self.client.force_authenticate(user=self.common_user)

    def test_list_missions(self):
        url = reverse('mission-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_accept_mission(self):
        url = reverse('mission-accept', kwargs={'pk': self.mission1.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.mission1.refresh_from_db()
        self.assertEqual(self.mission1.status, 'ACTIVE')
        self.assertEqual(self.mission1.assigned_to.id, self.common_user.id)

    def test_submit_feedback(self):
        # Primeiro aceitar a missão
        self.mission1.activate(self.common_user)
        
        url = reverse('mission-submit-feedback', kwargs={'pk': self.mission1.id})
        data = {'feedback_text': 'Ótimo site, fácil de usar!'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.mission1.refresh_from_db()
        self.assertEqual(self.mission1.status, 'COMPLETED')
        
        # Verificar se o feedback foi criado
        feedback = Feedback.objects.filter(mission=self.mission1).first()
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.feedback_text, data['feedback_text'])

    def test_submit_feedback_without_accepting(self):
        url = reverse('mission-submit-feedback', kwargs={'pk': self.mission1.id})
        data = {'feedback_text': 'Test feedback'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Mission not active or not assigned to you', str(response.data))

    def test_accept_already_accepted_mission(self):
        # Primeiro aceitar a missão
        self.mission1.activate(self.common_user)
        
        url = reverse('mission-accept', kwargs={'pk': self.mission1.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Mission not available', str(response.data))