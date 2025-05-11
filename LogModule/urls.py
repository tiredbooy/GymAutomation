from django.urls import path
from .views import LogAPIView

urlpatterns = [
    path('', LogAPIView.as_view()),
]
