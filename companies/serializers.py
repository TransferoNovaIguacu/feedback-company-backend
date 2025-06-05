from rest_framework import serializers
from companies.models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id',
            'commercial_name',
            'legal_name',
            'business_area',
            'cnpj',
            'website',
            'logo_url',
            'verified',
            'tokens_balance',
            'corporate_tax_id'
        ]
        read_only_fields = ['id', 'verified', 'tokens_balance']
