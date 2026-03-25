import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentication.models import PermissionMatrix

roles = ['SUPER_ADMIN', 'ADMIN', 'UNIT_ADMIN', 'MANAGER', 'SUPERVISOR', 'ACCOUNTANT', 'HR', 'EMPLOYEE']
modules = ['employee', 'production', 'attendance', 'advance', 'salary', 'master_data', 'reports']

for role in roles:
    for module in modules:
        PermissionMatrix.objects.get_or_create(
            role=role,
            module=module,
            defaults={'can_view': True, 'can_edit': True, 'can_delete': True}
        )

print("Permissions seeded.")
