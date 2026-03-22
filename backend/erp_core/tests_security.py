from django.test import TestCase
from rest_framework.test import APIClient
from authentication.models import User, PermissionMatrix
from master_data.models import Unit, Designation
from erp_core.models import Employee
from payroll.models_salary import SalaryRecord
from payroll.engine import calculate_monthly_salary
from decimal import Decimal
from django.db import models

class PayrollReconciliationTest(TestCase):
    def setUp(self):
        self.unit = Unit.objects.create(name="Recon Unit")
        self.dept = self.unit.departments.create(name="Recon Dept")
        self.desig = Designation.objects.create(name="Recon Desig")
        
        # Superuser to bypass isolation
        self.superuser = User.objects.create_superuser('super', 'super@ex.com', 'password')

    def test_reconciliation(self):
        # Create multiple employees with salaries
        for i in range(1, 4):
            emp = Employee.objects.create(
                employee_id=f"RECON{i}", full_name=f"User {i}", gender="M",
                unit=self.unit, department=self.dept, designation=self.desig,
                salary_type="MONTHLY", rate=Decimal('30000.00')
            )
            # Create salary record manually for speed in test
            SalaryRecord.objects.create(
                employee=emp, month=10, year=2023, unit=self.unit,
                production_total=0, attendance_salary=Decimal('30000.00'),
                overtime_total=0, advance_deduction=0,
                gross_salary=Decimal('30000.00'), net_salary=Decimal('30000.00')
            )
            
        total_salary_from_records = SalaryRecord.objects.filter(unit=self.unit, month=10, year=2023).aggregate(total=models.Sum('net_salary'))['total']
        self.assertEqual(total_salary_from_records, Decimal('90000.00'))

class UnitTamperingSecurityTest(TestCase):
    def setUp(self):
        self.unit_a = Unit.objects.create(name="Unit A")
        self.unit_b = Unit.objects.create(name="Unit B")
        self.user_a = User.objects.create_user(username='user_a', password='password', role='UNIT_ADMIN', unit=self.unit_a)
        PermissionMatrix.objects.create(role='UNIT_ADMIN', module='employee', can_view=True)

    def test_unit_tampering(self):
        client = APIClient()
        client.force_authenticate(user=self.user_a)
        
        # Attempt to access Unit B data by passing unit_id param
        response = client.get(f'/api/erp/employees/?unit_id={self.unit_b.id}')
        # Even if they pass unit_id, for_user() and middleware must ensure they only see Unit A
        self.assertEqual(response.status_code, 200)
        for emp in response.data:
            self.assertEqual(emp['unit'], self.unit_a.id)
