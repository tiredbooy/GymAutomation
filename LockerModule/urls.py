from django.urls import path
from .views import LockerAPIView

urlpatterns = [
    path('', LockerAPIView.as_view()),
]
