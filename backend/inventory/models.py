from django.db import models
from master_data.models import Unit

class Material(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    unit_of_measure = models.CharField(max_length=50) # e.g., Meters, Kg
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class StockRecord(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.material.name} - {self.quantity} in {self.unit.name}"
