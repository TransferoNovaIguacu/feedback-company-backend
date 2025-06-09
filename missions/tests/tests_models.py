from django.test import TestCase
from django.contrib.auth import get_user_model
from companies.models import Company
from plans.models import Plan, ContractedPlan
from missions.models import Mission, Feedback
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

from tokens.models import TokenWallet
from users.models import CommonUser

User = get_user_model()

class MissionModelTests(TestCase):
    def setUp(self):
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

    def test_mission_creation(self):
        mission = Mission.objects.create(
            contracted_plan=self.contracted_plan,
            mission_type='FEEDBACK',
            title='Test Mission',
            description='Test Description',
            url='http://test.com',
            status='PENDING'
        )
        self.assertEqual(mission.title, 'Test Mission')
        self.assertEqual(mission.status, 'PENDING')
        self.assertEqual(mission.contracted_plan, self.contracted_plan)

    def test_mission_activation(self):
        mission = Mission.objects.create(
            contracted_plan=self.contracted_plan,
            mission_type='FEEDBACK',
            title='Test Mission',
            description='Test Description',
            url='http://test.com',
            status='PENDING'
        )
        
        # Testar ativação bem-sucedida
        self.assertTrue(mission.activate(self.common_user))
        mission.refresh_from_db()
        self.assertEqual(mission.status, 'ACTIVE')
        self.assertEqual(mission.assigned_to, self.common_user)
        
        # Testar tentativa de reativação
        self.assertFalse(mission.activate(self.common_user))

    def test_mission_completion(self):
        mission = Mission.objects.create(
            contracted_plan=self.contracted_plan,
            mission_type='FEEDBACK',
            title='Test Mission',
            description='Test Description',
            url='http://test.com',
            status='PENDING'
        )
        mission.activate(self.common_user)
        
        # Testar conclusão bem-sucedida
        feedback_text = "Ótimo site, fácil de usar!"
        feedback = mission.complete(feedback_text)
        
        self.assertEqual(feedback.feedback_text, feedback_text)
        self.assertEqual(feedback.user, self.common_user)
        self.assertEqual(feedback.company, self.company)
        
        mission.refresh_from_db()
        self.assertEqual(mission.status, 'COMPLETED')
        self.assertEqual(self.contracted_plan.remaining_feedbacks, self.plan.feedbacks_available - 1)

    def test_feedback_creation(self):
        mission = Mission.objects.create(
            contracted_plan=self.contracted_plan,
            mission_type='FEEDBACK',
            title='Test Mission',
            description='Test Description',
            url='http://test.com',
            status='PENDING'
        )
        mission.activate(self.common_user)
        
        feedback = Feedback.objects.create(
            mission=mission,
            user=self.common_user,
            company=self.company,
            feedback_text="Test feedback"
        )
        
        self.assertEqual(feedback.user, self.common_user)
        self.assertEqual(feedback.company, self.company)
        self.assertEqual(feedback.mission, mission)
        
        # Testar relacionamentos reversos
        self.assertEqual(self.company.company_feedbacks.count(), 1)
        self.assertEqual(self.common_user.user_feedbacks.count(), 1)
        self.assertEqual(mission.feedbacks.count(), 1)