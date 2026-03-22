from django.db import models
from master_data.models import Unit, Department, Designation
from .managers import UnitIsolatedManager

class Employee(models.Model):
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))
    SALARY_TYPE_CHOICES = (
        ('PRODUCTION_WISE', 'Production Wise'),
        ('MONTHLY', 'Monthly'),
        ('DAILY', 'Daily'),
    )

    employee_id = models.CharField(max_length=50, unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, db_index=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    salary_type = models.CharField(max_length=20, choices=SALARY_TYPE_CHOICES)
    rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    branch_name = models.CharField(max_length=255, blank=True, null=True)
    
    user_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    status = models.BooleanField(default=True) # Active/Inactive
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UnitIsolatedManager()

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"
