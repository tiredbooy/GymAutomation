from django.urls import path
from .views import DataImportFromJsonConfigAPIView

urlpatterns = [
    path('import-initial-data/', DataImportFromJsonConfigAPIView.as_view(), name='import-initial-data'),
]
