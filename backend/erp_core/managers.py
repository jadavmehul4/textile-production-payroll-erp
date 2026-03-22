from django.db import models

class UnitIsolatedQuerySet(models.QuerySet):
    def for_user(self, user):
        if not user or not user.is_authenticated:
            return self.none()
        if user.is_superuser:
            return self
        return self.filter(unit_id=user.unit_id)

class UnitIsolatedManager(models.Manager):
    def get_queryset(self):
        return UnitIsolatedQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user)
