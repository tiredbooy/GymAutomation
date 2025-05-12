from django.contrib import admin
from .models import GenMembershipType, GenPersonRole, GenShift, GenMember, GenPerson, SecUser

admin.site.register(GenMembershipType)
admin.site.register(GenPersonRole)
admin.site.register(GenShift)
admin.site.register(GenMember)
admin.site.register(GenPerson)
admin.site.register(SecUser)