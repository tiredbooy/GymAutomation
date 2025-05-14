from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Locker
from .serializers import LockerSerializer

class LockerAPIView(APIView):
    def get(self, request):
        locker_id = request.query_params.get('id')
        if locker_id:
            try:
                locker = Locker.objects.get(id=locker_id)
                serializer = LockerSerializer(locker)
                return Response(serializer.data)
            except Locker.DoesNotExist:
                return Response({'error': 'Locker not found.'}, status=status.HTTP_404_NOT_FOUND)

        filters = Q()
        filter_fields = ['is_vip', 'is_open', 'user', 'full_name']

        for field in filter_fields:
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{field: value})

        lockers = Locker.objects.filter(filters)

        # Pagination
        try:
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 10))
            if page < 1 or limit < 1:
                raise ValueError
        except ValueError:
            return Response({'error': 'Invalid pagination parameters'}, status=status.HTTP_400_BAD_REQUEST)

        start = (page - 1) * limit
        end = start + limit
        paginated_lockers = lockers[start:end]

        serializer = LockerSerializer(paginated_lockers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LockerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        locker_id = request.query_params.get('id')
        if not locker_id:
            return Response({'error': 'ID query param required for PATCH.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            locker = Locker.objects.get(id=locker_id)
        except Locker.DoesNotExist:
            return Response({'error': 'Locker not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LockerSerializer(locker, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        locker_id = request.query_params.get('id')
        if not locker_id:
            return Response({'error': 'ID query param required for DELETE.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            locker = Locker.objects.get(id=locker_id)
            locker.delete()
            return Response({'message': 'Locker deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Locker.DoesNotExist:
            return Response({'error': 'Locker not found.'}, status=status.HTTP_404_NOT_FOUND)
