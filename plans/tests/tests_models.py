# Create your tests here.

from django.test import TestCase
from django.contrib.auth import get_user_model
from plans.models import Plan, ContractedPlan
from companies.models import Company

User = get_user_model()

class PlanModelTest(TestCase):
    def setUp(self):
        self.plan = Plan.objects.create(
            name="Plano Básico",
            description="Plano inicial para pequenas empresas",
            token_value=10.00,
            feedbacks_available=50,
            quests_available=20,
            reward_percentage=0.6
        )

    def test_plan_creation(self):
        self.assertEqual(self.plan.name, "Plano Básico")
        self.assertEqual(self.plan.token_value, 10.00)
        self.assertTrue(self.plan.is_active)

class ContractedPlanTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="company@example.com",
            password="testpass123"
        )
        self.company = Company.objects.create(
            user=self.user,
            name="Empresa Teste"
        )
        self.plan = Plan.objects.create(
            name="Plano Teste",
            description="Descrição",
            token_value=5.00,
            feedbacks_available=30,
            quests_available=10
        )

    def test_contracted_plan_creation(self):
        contracted = ContractedPlan.objects.create(
            company=self.company,
            plan=self.plan,
            remaining_feedbacks=self.plan.feedbacks_available,
            remaining_quests=self.plan.quests_available
        )
        
        self.assertEqual(contracted.company, self.company)
        self.assertEqual(contracted.remaining_feedbacks, 30)
        self.assertTrue(contracted.is_active)