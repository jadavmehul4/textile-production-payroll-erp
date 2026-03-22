from django.test import TestCase
from rest_framework.test import APIClient
from authentication.models import User, PermissionMatrix
from master_data.models import Unit, Buyer, Item, Operation, Designation
from erp_core.models import Employee

class UnitIsolationTest(TestCase):
    def setUp(self):
        self.unit_a = Unit.objects.create(name="Unit A")
        self.unit_b = Unit.objects.create(name="Unit B")
        
        self.admin_a = User.objects.create_user(
            username='admin_a', password='password', role='UNIT_ADMIN', unit=self.unit_a
        )
        self.admin_b = User.objects.create_user(
            username='admin_b', password='password', role='UNIT_ADMIN', unit=self.unit_b
        )
        
        # Seed permissions
        PermissionMatrix.objects.create(role='UNIT_ADMIN', module='employee', can_view=True, can_edit=True)
        
        # Create data for Unit B
        self.dept_b = self.unit_b.departments.create(name="Dept B")
        self.desig = Designation.objects.create(name="Desig")
        Employee.objects.create(
            employee_id="EMP_B", full_name="User B", gender="M",
            unit=self.unit_b, department=self.dept_b, designation=self.desig,
            salary_type="MONTHLY", rate=10000
        )

    def test_isolation(self):
        client = APIClient()
        client.force_authenticate(user=self.admin_a)
        
        # Admin A should not see Employee from Unit B
        response = client.get('/api/erp/employees/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
        
        # Admin B should see it
        client.force_authenticate(user=self.admin_b)
        response = client.get('/api/erp/employees/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
