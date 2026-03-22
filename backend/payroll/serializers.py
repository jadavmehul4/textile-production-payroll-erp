from rest_framework import serializers
from .models import Advance

class AdvanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.full_name')
    class Meta:
        model = Advance
        fields = '__all__'
