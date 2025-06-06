
import datetime
from rest_framework.test import APIRequestFactory
from users.models import User
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from users.models import UserType
from companies.models import Company

from missions.models import (
    ContractedPlan,
    Mission,
    Feedback,
    QuizAnswer,
    MissionType,
    Rating,
    ApprovalStatus
)
from missions.serializers import (
    MissionSerializer,
    FeedbackSerializer,
    QuizAnswerSerializer
)


class MissionSerializerTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            email="company@example.com",
            password="test123",
            commercial_name="Test Company",
            legal_name="Test Company LTDA",
            cnpj="12345678000199"
        )

        self.plan = ContractedPlan.objects.create(
            company=self.company,
            plan_type="PRO",
            start_date=timezone.now().date() - timedelta(days=1),  # começa ontem
            end_date=timezone.now().date() + timedelta(days=30),   # termina em 30 dias
            is_active=True
        )

        self.mission = Mission.objects.create(
            company=self.company,
            contracted_plan=self.plan,
            mission_type=MissionType.FEEDBACK,
            title="Test Mission",
            description="Test mission description",
            tokens_reward=50.0,
            expiration_date=timezone.now() + timedelta(days=15),
            estimated_time=30
        )

    def test_basic_serialization(self):
        serializer = MissionSerializer(instance=self.mission)
        data = serializer.data

        self.assertEqual(data['title'], "Test Mission")
        self.assertEqual(data['mission_type'], MissionType.FEEDBACK)
        self.assertEqual(float(data['tokens_reward']), 50.0)
        self.assertEqual(data['company']['commercial_name'], "Test Company")

    def test_dates_format(self):
        serializer = MissionSerializer(instance=self.mission)
        data = serializer.data

        self.assertIn('T', data['creation_date'])
        self.assertIn('T', data['expiration_date'])

    def test_is_active_logic(self):
        self.assertTrue(MissionSerializer(instance=self.mission).data['is_active'])

        expired_mission = Mission.objects.create(
            company=self.company,
            contracted_plan=self.plan,
            mission_type=MissionType.QUIZ,
            title="Expired Mission",
            description="Expired",
            tokens_reward=10,
            expiration_date=timezone.now() - timedelta(days=1),
            estimated_time=10
        )
        self.assertFalse(MissionSerializer(instance=expired_mission).data['is_active'])

    def test_read_only_fields_auto_assignment(self):
        class MockRequest:
            def __init__(self, user):
                self.user = user
                

        serializer = MissionSerializer(
            data={
                'mission_type': MissionType.QUIZ,
                'title': "Auto Assignment Mission",
                'description': "Testing auto assignment",
                'tokens_reward': 20.0,
                'expiration_date': (timezone.now() + timedelta(days=5)).isoformat(),
                'estimated_time': 15,
            },
            context={'request': MockRequest(self.company)}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        mission = serializer.save()
        self.assertEqual(mission.company, self.company)
        self.assertEqual(mission.contracted_plan, self.plan)

    def test_partial_update(self):
        serializer = MissionSerializer(
            instance=self.mission,
            data={'title': 'Updated Title'},
            partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        mission = serializer.save()
        self.assertEqual(mission.title, 'Updated Title')

    def test_validation_errors(self):
        serializer = MissionSerializer(
            data={
                'mission_type': MissionType.FEEDBACK,
                'title': "",
                'description': "",
                'tokens_reward': -5,
                'expiration_date': "",
                'estimated_time': None
            },
            context={'request': type('Request', (), {'user': self.company})}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('tokens_reward', serializer.errors)
        self.assertIn('title', serializer.errors)
        self.assertIn('description', serializer.errors)

    def test_mission_creation(self):
        initial_count = Mission.objects.count()

        class MockRequest:
            def __init__(self, user):
                self.user = user
                

        serializer = MissionSerializer(
            data={
                'mission_type': MissionType.QUIZ,
                'title': "Created Mission",
                'description': "Created via serializer",
                'tokens_reward': 25.0,
                'expiration_date': (timezone.now() + timedelta(days=7)).isoformat(),
                'estimated_time': 20,
            },
            context={'request': MockRequest(self.company)}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        mission = serializer.save()
        self.assertEqual(Mission.objects.count(), initial_count + 1)
        self.assertEqual(mission.company, self.company)
        self.assertEqual(mission.contracted_plan, self.plan)


class FeedbackSerializerTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            email="feedback@example.com",
            password="test123",
            commercial_name="Feedback Company",
            legal_name="Feedback Company LTDA",
            cnpj="98765432000199"
        )

        self.plan = ContractedPlan.objects.create(
            company=self.company,
            plan_type="PRO",
            start_date=timezone.now().date() - timedelta(days=1),  # começa ontem
            end_date=timezone.now().date() + timedelta(days=30),   # termina em 30 dias
            is_active=True
        )

        self.mission = Mission.objects.create(
            company=self.company,
            contracted_plan=self.plan,
            mission_type=MissionType.FEEDBACK,
            title="Feedback Mission",
            description="Feedback mission",
            tokens_reward=15.0,
            expiration_date=timezone.now() + timedelta(days=10),
            estimated_time=15
        )

    def test_feedback_creation(self):
        serializer = FeedbackSerializer(
            data={
                'content': "Great mission!",
                'rating': Rating.GOOD,
                'tokens_rewarded': 10.0,
                'status': ApprovalStatus.PENDING
            },
            context={
                'request': type('Request', (), {'user': self.company}),
                'mission': self.mission
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        feedback = serializer.save()
        self.assertEqual(feedback.company, self.company)
        self.assertEqual(feedback.mission, self.mission)


class QuizAnswerSerializerTests(TestCase):
    def setUp(self):
        # Cria um usuário e a empresa relacionada
        self.user = User.objects.create_user(email="test@example.com", password="123456", user_type="COMPANY")
        self.company = Company.objects.create(user_ptr=self.user, commercial_name="Test Co", legal_name="Test Co LTDA", cnpj="12345678000100", verified=True)
        
         # Cria um plano ativo para a empresa
        self.plan = ContractedPlan.objects.create(
            company=self.company,
            plan_type="PRO",
            start_date=timezone.now().date() - timedelta(days=1),
            end_date=timezone.now().date() + timedelta(days=30),
            is_active=True
        )

        # Cria uma missão fictícia associada à empresa
        self.mission = Mission.objects.create(
            company=self.company,
            contracted_plan=self.plan,
            mission_type="QUIZ",
            title="Missão Teste",
            description="Descrição",
            tokens_reward=10,
            expiration_date=timezone.now() + datetime.timedelta(days=30),
            estimated_time=5
        )

        self.factory = APIRequestFactory()
        self.request = self.factory.post("/fake-url")
        self.request.user = self.user

    def test_quiz_answer_creation(self):
        data = {
            "answers": {"q1": "a", "q2": "b"},
            "tokens_rewarded": 10,
            "is_verified": False
        }

        # 👇 Aqui está a correção importante!
        serializer = QuizAnswerSerializer(
            data=data,
            context={
                "request": self.request,
                "mission": self.mission  # <--- ESSENCIAL PARA FUNCIONAR
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        quiz_answer = serializer.save()

        self.assertEqual(quiz_answer.company, self.company)
        self.assertEqual(quiz_answer.mission, self.mission)
        self.assertEqual(quiz_answer.tokens_rewarded, 10)

