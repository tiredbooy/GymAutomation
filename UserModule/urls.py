from django.urls import path
from .views import DynamicAPIView

urlpatterns = [
    path('', DynamicAPIView.as_view()),
]
