from rest_framework import serializers
from .models import Log

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['id', 'user', 'full_name', 'is_online', 'entry_time', 'exit_time']
