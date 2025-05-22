from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import GenShift, SecUser, GenPerson, GenPersonRole, GenMember, GenMembershipType
from .serializers import (
    GenShiftSerializer, SecUserSerializer, GenPersonSerializer, GenPersonRoleSerializer,
    GenMemberSerializer, GenMembershipTypeSerializer
)



class DynamicAPIView(APIView):

    def get_model(self, action):
        """Return the correct model based on the action query."""
        if action == 'shift':
            return GenShift
        elif action == 'user':
            return SecUser
        elif action == 'person':
            return GenPerson
        elif action == 'role':
            return GenPersonRole
        elif action == 'member':
            return GenMember
        elif action == 'membership_type':
            return GenMembershipType
        else:
            return None

    def get_serializer(self, model):
        """Return the correct serializer for the model."""
        if model == GenShift:
            return GenShiftSerializer
        elif model == SecUser:
            return SecUserSerializer
        elif model == GenPerson:
            return GenPersonSerializer
        elif model == GenPersonRole:
            return GenPersonRoleSerializer
        elif model == GenMember:
            return GenMemberSerializer
        elif model == GenMembershipType:
            return GenMembershipTypeSerializer
        else:
            return None

    def get(self, request):
        """Handle GET request with filtering and pagination."""
        action = request.query_params.get('action')
        model = self.get_model(action)
        if not model:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        filters = Q()
        filter_fields = []

        # Define the filter fields and primary key for each action
        primary_key_field = None
        if action == 'shift':
            filter_fields = ['shift_id', 'shift_desc']
            primary_key_field = 'shift_id'
        elif action == 'user':
            filter_fields = ['user_id', 'person', 'username', 'is_admin', 'shift', 'is_active']
            primary_key_field = 'user_id'
        elif action == 'person':
            filter_fields = ['person_id', 'first_name', 'last_name', 'full_name', 'father_name', 'gender',
                             'national_code', 'nidentity', 'person_image', 'thumbnail_image', 'birth_date',
                             'tel', 'mobile', 'email', 'has_insurance', 'user']
            primary_key_field = 'person_id'
        elif action == 'role':
            filter_fields = ['role_id', 'role_desc']
            primary_key_field = 'role_id'
        elif action == 'member':
            filter_fields = ['member_id', 'card_no', 'person', 'role_id', 'user', 'shift', 'is_black_list',
                             'membership_datetime', 'minutiae', 'minutiae2', 'minutiae3',
                             'face_template_1', 'face_template_2', 'face_template_3',
                             'face_template_4', 'face_template_5']
            primary_key_field = 'member_id'
        elif action == 'membership_type':
            filter_fields = ['membership_type_id', 'membership_type_desc']
            primary_key_field = 'membership_type_id'

        # Filter by the primary key if "id" param is present
        object_id = request.query_params.get('id')
        if object_id and primary_key_field:
            filters &= Q(**{primary_key_field: object_id})

        # Apply additional filters from query params
        for field in filter_fields:
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{field: value})

        # Apply filtering
        queryset = model.objects.filter(filters)

        # Apply ordering
        order_by = request.query_params.get('order_by')
        if order_by == 'latest':
            queryset = queryset.order_by(f'-{primary_key_field}')
        elif order_by == 'earlier':
            queryset = queryset.order_by(f'{primary_key_field}')

        # Handle pagination
        try:
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 10))
        except ValueError:
            return Response({'error': 'Invalid pagination values'}, status=status.HTTP_400_BAD_REQUEST)

        total_items = queryset.count()
        total_pages = (total_items + limit - 1) // limit

        start = (page - 1) * limit
        end = start + limit
        paginated_queryset = queryset[start:end]

        serializer = self.get_serializer(model)(paginated_queryset, many=True)

        return Response({
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'items': serializer.data
        })

    def post(self, request):
        """Handle POST request to create objects."""
        action = request.query_params.get('action')
        model = self.get_model(action)
        if not model:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and create the object
        serializer = self.get_serializer(model)(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        action = request.query_params.get('action')
        model = self.get_model(action)
        if not model:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        # Map primary key field per action
        primary_key_field = None
        if action == 'shift':
            primary_key_field = 'shift_id'
        elif action == 'user':
            primary_key_field = 'user_id'
        elif action == 'person':
            primary_key_field = 'person_id'
        elif action == 'role':
            primary_key_field = 'role_id'
        elif action == 'member':
            primary_key_field = 'member_id'
        elif action == 'membership_type':
            primary_key_field = 'membership_type_id'

        object_id = request.query_params.get('id')
        if not object_id:
            return Response({'error': 'ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Build filter kwargs dynamically
        filter_kwargs = {primary_key_field: object_id} if primary_key_field else {}

        try:
            obj = model.objects.get(**filter_kwargs)
        except model.DoesNotExist:
            return Response({'error': f'{action} not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(model)(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        action = request.query_params.get('action')
        model = self.get_model(action)
        if not model:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        # Map primary key field per action
        primary_key_field = None
        if action == 'shift':
            primary_key_field = 'shift_id'
        elif action == 'user':
            primary_key_field = 'user_id'
        elif action == 'person':
            primary_key_field = 'person_id'
        elif action == 'role':
            primary_key_field = 'role_id'
        elif action == 'member':
            primary_key_field = 'member_id'
        elif action == 'membership_type':
            primary_key_field = 'membership_type_id'

        object_id = request.query_params.get('id')
        if not object_id:
            return Response({'error': 'ID parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Build filter kwargs dynamically
        filter_kwargs = {primary_key_field: object_id} if primary_key_field else {}

        try:
            instance = model.objects.get(**filter_kwargs)
        except model.DoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        instance.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

