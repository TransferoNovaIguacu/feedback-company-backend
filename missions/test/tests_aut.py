from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from companies.models import Company
from missions.models import Mission, Feedback, QuizAnswer, Contracted_Plan
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()


class BaseTestCase(APITestCase):
    def setUp(self):
        # Configuração comum para todos os testes
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.company = Company.objects.create(
            commercial_name='Test Company'
        )
        # Criar plano contratado com os campos que existem no seu modelo
        today = timezone.now().date()
        self.plan = Contracted_Plan.objects.create(
            company=self.company,
            # Use apenas os campos que existem no seu modelo ContractedPlan
            # Exemplo básico - ajuste conforme seu modelo real
            # Se seu modelo não tem esses campos, remova-os
             plan_type='BASIC',  # Remova se não existir
             start_date=today,  # Remova se não existir
             end_date=today + timedelta(days=30), 
             is_active=True  # Remova se não existir
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


class MissionViewSetTests(APITestCase):
    def setUp(self):
        # Configuração inicial para todos os testes
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.company = Company.objects.create(
            commercial_name='Test Company'
            # Removido o parâmetro user que não existe no modelo
        )
        self.plan = Contracted_Plan.objects.create(
            company=self.company,
            plan_type='BASIC',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date(),
            is_active=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Criar uma missão de exemplo
        self.mission = Mission.objects.create(
            company=self.company,
            contracted_plan=self.plan,
            mission_type='FB',
            title='Test Mission',
            description='Test Description',
            tokens_reward=10.50,
            expiration_date=timezone.now() + timedelta(days=7),
            estimated_time=30
        )
        
        # URLs
        self.mission_list_url = reverse('mission-list')
        self.mission_detail_url = reverse('mission-detail', args=[self.mission.id])

    # ... (restante dos testes de Mission permanecem iguais)

class FeedbackViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='feedback@example.com',
            password='testpass123'
        )
        self.company = Company.objects.create(
            commercial_name='Feedback Company'
            # Removido o parâmetro user que não existe no modelo
        )
        self.plan = Contracted_Plan.objects.create(
            company=self.company,
            plan_type='PRO',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date(),
            is_active=True
        )
        self.mission = Mission.objects.create(
            company=self.company,
            contracted_plan=self.plan,
            mission_type='FB',
            title='Feedback Mission',
            description='Mission for feedback',
            tokens_reward=5.00,
            expiration_date=timezone.now() + timedelta(days=7),
            estimated_time=20
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Criar feedback de exemplo
        self.feedback = Feedback.objects.create(
            company=self.company,
            mission=self.mission,
            content='Initial feedback content',
            rating='good',
            tokens_rewarded=5.00,
            status='PENDING'
        )
        
        # URLs
        self.feedback_list_url = reverse('feedback-list')
        self.feedback_detail_url = reverse('feedback-detail', args=[self.feedback.id])

    # ... (restante dos testes de Feedback permanecem iguais)

class QuizAnswerViewSetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        
        # Criar missão de exemplo
        self.mission = Mission.objects.create(
            company=self.company,
            contracted_plan=self.plan,
            mission_type='QZ',
            title='Quiz Mission',
            description='Mission with quiz',
            tokens_reward=20.00,
            expiration_date=timezone.now() + timedelta(days=7),
            estimated_time=45
        )
        
        # Criar resposta de quiz de exemplo
        self.quiz_answer = QuizAnswer.objects.create(
            company=self.company,
            mission=self.mission,
            answers={'q1': 'A', 'q2': 'B', 'q3': 'C'},
            tokens_rewarded=20.00,
            is_verified=True
        )
        
        # URLs
        self.quiz_list_url = reverse('quizanswer-list')
        self.quiz_detail_url = reverse('quizanswer-detail', args=[self.quiz_answer.id])

    def test_list_quiz_answers(self):
        """Testa a listagem de respostas de quiz"""
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['answers'], {'q1': 'A', 'q2': 'B', 'q3': 'C'})

    def test_verify_quiz_answer(self):
        """Testa a verificação de uma resposta de quiz"""
        data = {'is_verified': False}
        response = self.client.patch(self.quiz_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.quiz_answer.refresh_from_db()
        self.assertFalse(self.quiz_answer.is_verified)