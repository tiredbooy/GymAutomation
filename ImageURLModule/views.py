from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.conf import settings

class ImageUploadView(APIView):
    def post(self, request, *args, **kwargs):
        if 'image' not in request.FILES:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        files = request.FILES.getlist('image')
        image_urls = []

        for file in files:
            file_path = default_storage.save(f"images/{file.name}", file)
            # Correctly construct the full URL
            full_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)
            image_urls.append(full_url)

        return Response({"image_urls": image_urls}, status=status.HTTP_201_CREATED)
