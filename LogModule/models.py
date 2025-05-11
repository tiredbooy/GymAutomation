from django.db import models
from django.utils.timezone import now
from UserModule.models import GenMember


class Log(models.Model):
    user = models.ForeignKey(GenMember, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, null=True, blank=True)

    is_online = models.BooleanField(default=True)
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)  # This will be set when 'is_online' changes to False

    def save(self, *args, **kwargs):
        if not self.is_online and self.exit_time is None:
            self.exit_time = now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Log for {self.full_name or self.user.username} - {'Online' if self.is_online else 'Offline'}"
