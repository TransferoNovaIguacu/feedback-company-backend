from rest_framework import serializers
from .models import Mission, Feedback, QuizAnswer
from companies.models import Company
import re
from rest_framework import serializers
from .models import QuizAnswer
from companies.serializers import CompanySerializer


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'commercial_name']


class MissionSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    contracted_plan = serializers.PrimaryKeyRelatedField(read_only=True)
    is_active = serializers.BooleanField(read_only=True) 

    class Meta:
        model = Mission
        fields = [
            'id', 'company', 'contracted_plan', 'mission_type',
            'title', 'description', 'tokens_reward',
            'is_active', 'creation_date', 'expiration_date',
            'estimated_time'
        ]
        extra_kwargs = {
            'company': {'read_only': True},
            'contracted_plan': {'read_only': True},
            'creation_date': {'read_only': True},
        }
        
    def create(self, validated_data):
        company = self.context['request'].user
        validated_data['company'] = company
        
        # Corrigido: Acessar o plano ativo corretamente
        if hasattr(company, 'active_plan'):
            validated_data['contracted_plan'] = company.active_plan
        else:
            # Se não houver plano ativo, pegue o último plano criado como fallback
            validated_data['contracted_plan'] = company.plans.order_by('-start_date').first()
            
        if not validated_data['contracted_plan']:
            raise serializers.ValidationError("Company doesn't have an active plan")
            
        return super().create(validated_data)


class FeedbackSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    mission = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Feedback
        fields = [
            'id', 'company', 'mission', 'content', 'rating',
            'tokens_rewarded', 'submission_date', 'status'
        ]
    
    def create(self, validated_data):
        validated_data['company'] = self.context['request'].user.company
        validated_data['mission'] = self.context['mission']
        return super().create(validated_data)



class QuizAnswerSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    mission = serializers.PrimaryKeyRelatedField(read_only=True)

    titulo = serializers.CharField(source='mission.title', read_only=True)
    descricao = serializers.CharField(source='mission.description', read_only=True)

    # Entrada: usuário envia "perguntas"
    perguntas = serializers.ListField(write_only=True)

    # Saída: servidor responde com "perguntas_out"
    perguntas_out = serializers.SerializerMethodField()

    answers = serializers.JSONField(read_only=True)

    class Meta:
        model = QuizAnswer
        fields = [
            'id', 'company', 'mission',
            'titulo', 'descricao',
            'perguntas', 'perguntas_out', 'answers',
            'completion_date', 'tokens_rewarded', 'is_verified'
        ]

    def get_perguntas_out(self, obj):
        """
        Transforma answers em uma lista formatada para a resposta
        """
        perguntas = []
        answers = obj.answers or {}
        for key, opcao in answers.items():
            perguntas.append({
                "titulo": f"Pergunta {key}",
                "descricao": f"Descrição para {key}",
                "opcao": opcao
            })
        return perguntas

    def to_internal_value(self, data):
        """
        Transforma 'perguntas' recebidas do cliente em dict 'answers'
        """
        perguntas = data.get('perguntas', [])
        answers = {}

        for pergunta in perguntas:
            titulo = pergunta.get('titulo', '')
            # Verifica tanto 'opção' (com acento) quanto 'opcao' (sem acento)
            opcao = pergunta.get('opcao') or pergunta.get('opção')
            match = re.search(r'\d+', titulo)
            if match and opcao:
                question_number = match.group()
                answers[question_number] = opcao

        mutable_data = data.copy()
        mutable_data['answers'] = answers
        return super().to_internal_value(mutable_data)

    def create(self, validated_data):
        validated_data['company'] = self.context['request'].user.company
        validated_data['mission'] = self.context['mission']
        return super().create(validated_data)