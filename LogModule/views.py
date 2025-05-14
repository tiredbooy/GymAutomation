from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Log
from .serializers import LogSerializer


class LogAPIView(APIView):
    def get(self, request):
        log_id = request.query_params.get('id')
        if log_id:
            try:
                log = Log.objects.get(id=log_id)
                serializer = LogSerializer(log)
                return Response(serializer.data)
            except Log.DoesNotExist:
                return Response({'error': 'Log not found.'}, status=status.HTTP_404_NOT_FOUND)

        filters = Q()
        filter_fields = ['user', 'full_name', 'is_online', 'entry_time', 'exit_time']

        for field in filter_fields:
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{field: value})

        logs = Log.objects.filter(filters)

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
        paginated_logs = logs[start:end]

        serializer = LogSerializer(paginated_logs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        log_id = request.query_params.get('id')
        if not log_id:
            return Response({'error': 'ID query param required for PATCH.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            log = Log.objects.get(id=log_id)
        except Log.DoesNotExist:
            return Response({'error': 'Log not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LogSerializer(log, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        log_id = request.query_params.get('id')
        if not log_id:
            return Response({'error': 'ID query param required for DELETE.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            log = Log.objects.get(id=log_id)
            log.delete()
            return Response({'message': 'Log deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Log.DoesNotExist:
            return Response({'error': 'Log not found.'}, status=status.HTTP_404_NOT_FOUND)
