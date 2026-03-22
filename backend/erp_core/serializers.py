from rest_framework import serializers
from .models import Employee
from authentication.models import User
from django.utils.crypto import get_random_string

class EmployeeSerializer(serializers.ModelSerializer):
    unit_name = serializers.ReadOnlyField(source='unit.name')
    department_name = serializers.ReadOnlyField(source='department.name')
    designation_name = serializers.ReadOnlyField(source='designation.name')

    class Meta:
        model = Employee
        fields = '__all__'

    def create(self, validated_data):
        employee = super().create(validated_data)
        
        # Auto-generate User for the employee
        user_id = employee.full_name.lower().replace(' ', '') + employee.employee_id[-4:]
        password = get_random_string(length=8)
        
        user = User.objects.create_user(
            username=user_id,
            password=password,
            role='EMPLOYEE',
            unit=employee.unit,
            employee_id_ref=employee.employee_id
        )
        
        employee.user_id = user_id
        employee.save()
        
        # In a real scenario, you'd securely communicate the password
        print(f"Generated User: {user_id}, Password: {password}") 
        
        return employee
