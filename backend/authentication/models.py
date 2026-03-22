from django.contrib.auth.models import AbstractUser
from django.db import models
from master_data.models import Unit

class User(AbstractUser):
    ROLE_CHOICES = (
        ('SUPER_ADMIN', 'Super Admin'),
        ('ADMIN', 'Admin'),
        ('UNIT_ADMIN', 'Unit Admin'),
        ('MANAGER', 'Manager'),
        ('SUPERVISOR', 'Supervisor'),
        ('ACCOUNTANT', 'Accountant'),
        ('HR', 'HR'),
        ('EMPLOYEE', 'Employee'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    employee_id_ref = models.CharField(max_length=50, blank=True, null=True) # Reference to business Employee ID
    is_force_password_change = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class PermissionMatrix(models.Model):
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    module = models.CharField(max_length=50) # e.g., 'production', 'salary'
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    field_permissions = models.JSONField(default=dict) # e.g., {"rate": "hidden"}

    class Meta:
        unique_together = ('role', 'module')
