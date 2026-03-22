from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=50)
    module = models.CharField(max_length=100)
    action = models.CharField(max_length=50) # CREATE, UPDATE, DELETE
    target_id = models.CharField(max_length=100)
    old_value = models.JSONField(null=True)
    new_value = models.JSONField(null=True)
    ip_address = models.GenericIPAddressField(null=True)
    device_fingerprint = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        permissions = [
            ("view_audit_logs", "Can view audit logs")
        ]

    def __str__(self):
        return f"{self.user} - {self.module} - {self.action} - {self.timestamp}"
