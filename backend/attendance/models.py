from django.db import models
from master_data.models import Unit
from erp_core.models import Employee

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('PRESENT', 'Present'),
        ('HALF_DAY', 'Half Day'),
        ('ABSENT', 'Absent'),
        ('LEAVE', 'Leave'),
        ('HOLIDAY', 'Holiday'),
    )
    date = models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    
    in_time = models.TimeField(null=True, blank=True)
    out_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('date', 'employee')

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.status}"
