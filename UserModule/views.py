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
        """Handle GET request with filtering."""
        action = request.query_params.get('action')
        model = self.get_model(action)
        if not model:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        filters = Q()
        filter_fields = []

        # Define the filter fields based on the action
        if action == 'shift':
            filter_fields = ['shift_id', 'shift_desc']
        elif action == 'user':
            filter_fields = ['user_id', 'person', 'username', 'is_admin', 'shift', 'is_active']
        elif action == 'person':
            filter_fields = ['person_id', 'first_name', 'last_name', 'full_name', 'father_name', 'gender', 'national_code',
                             'nidentity', 'person_image', 'thumbnail_image', 'birth_date', 'tel', 'mobile', 'email', 'has_insurance',
                             'user']
        elif action == 'role':
            filter_fields = ['role_id', 'role_desc']
        elif action == 'member':
            filter_fields = ['member_id', 'card_no', 'person', 'role_id', 'user', 'shift', 'is_black_list', 'membership_datetime',
                             'minutiae', 'minutiae2', 'minutiae3', 'face_template_1', 'face_template_2', 'face_template_3',
                             'face_template_4', 'face_template_5']
        elif action == 'membership_type':
            filter_fields = ['membership_type_id', 'membership_type_desc']

        # Apply the filters based on query params
        for field in filter_fields:
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{field: value})

        objects = model.objects.filter(filters)
        serializer = self.get_serializer(model)(objects, many=True)
        return Response(serializer.data)

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
        """Handle PATCH request to update objects."""
        action = request.query_params.get('action')
        model = self.get_model(action)
        if not model:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        object_id = request.query_params.get('id')
        if not object_id:
            return Response({'error': 'ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = model.objects.get(id=object_id)
        except model.DoesNotExist:
            return Response({'error': f'{action} not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Partial update
        serializer = self.get_serializer(model)(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Handle DELETE request to delete objects."""
        action = request.query_params.get('action')
        model = self.get_model(action)
        if not model:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        object_id = request.query_params.get('id')
        if not object_id:
            return Response({'error': 'ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = model.objects.get(id=object_id)
        except model.DoesNotExist:
            return Response({'error': f'{action} not found.'}, status=status.HTTP_404_NOT_FOUND)

        obj.delete()
        return Response({'message': f'{action} deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
