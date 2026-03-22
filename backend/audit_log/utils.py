from erp_core.models import Employee
from production.models import ProductionEntry
from attendance.models import Attendance
from payroll.models import Advance, SalaryRecord
from audit_log.models import AuditLog
from django.db import models

class AuditManager:
    @staticmethod
    def log(user, module, action, target_id, old_value=None, new_value=None, request=None):
        ip = None
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

        AuditLog.objects.create(
            user=user,
            role=user.role if user else 'SYSTEM',
            module=module,
            action=action,
            target_id=str(target_id),
            old_value=old_value,
            new_value=new_value,
            ip_address=ip
        )
