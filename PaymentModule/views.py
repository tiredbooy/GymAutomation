from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Payment
from .serializers import PaymentSerializer


class PaymentAPIView(APIView):
    def get(self, request):
        payment_id = request.query_params.get('id')
        if payment_id:
            try:
                payment = Payment.objects.get(id=payment_id)
                serializer = PaymentSerializer(payment)
                return Response(serializer.data)
            except Payment.DoesNotExist:
                return Response({'error': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)

        filters = Q()

        # Exact match filters
        for field in ['user', 'price', 'payment_date']:
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{field: value})

        # Partial match filters
        for field in ['duration', 'paid_method', 'payment_status', 'full_name']:
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{f"{field}__icontains": value})

        # Payment date range filter
        start_date = request.query_params.get('from')
        end_date = request.query_params.get('to')
        if start_date and end_date:
            filters &= Q(payment_date__range=[start_date, end_date])
        elif start_date:
            filters &= Q(payment_date__gte=start_date)
        elif end_date:
            filters &= Q(payment_date__lte=end_date)

        payments = Payment.objects.filter(filters)

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
        paginated_payments = payments[start:end]

        serializer = PaymentSerializer(paginated_payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        payment_id = request.query_params.get('id')
        if not payment_id:
            return Response({'error': 'ID query param required for PATCH.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        payment_id = request.query_params.get('id')
        if not payment_id:
            return Response({'error': 'ID query param required for DELETE.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(id=payment_id)
            payment.delete()
            return Response({'message': 'Payment deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)
