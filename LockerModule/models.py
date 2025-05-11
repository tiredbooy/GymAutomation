from django.db import models
from UserModule.models import GenPerson

class Locker(models.Model):
    is_vip = models.BooleanField(default=False)
    is_open = models.BooleanField(default=False)

    log = models.JSONField(null=True,
                           blank=True)  # Stores a list of log entries, e.g., [{"full_name": "John Doe", "datetime": "2025-05-08T12:30:00"}]

    user = models.ForeignKey(GenPerson, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Locker {self.id} - {'VIP' if self.is_vip else 'Regular'}"
