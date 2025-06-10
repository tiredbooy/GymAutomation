from rest_framework import serializers
import base64
from .models import GenShift, SecUser, GenPerson, GenPersonRole, GenMember, GenMembershipType


class Base64BinaryField(serializers.Field):
    def to_internal_value(self, data):
        try:
            return base64.b64decode(data)
        except Exception:
            raise serializers.ValidationError("Invalid base64-encoded data.")

    def to_representation(self, value):
        if value is not None:
            return base64.b64encode(value).decode('utf-8')
        return None


class GenShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenShift
        fields = ['id', 'shift_desc']


class SecUserSerializer(serializers.ModelSerializer):
    creation_datetime = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SecUser
        fields = ['id', 'person', 'username', 'password', 'is_admin', 'shift', 'is_active', 'creation_datetime']


class GenPersonSerializer(serializers.ModelSerializer):
    creation_datetime = serializers.DateTimeField(read_only=True)
    person_image = Base64BinaryField(required=False, allow_null=True)
    thumbnail_image = Base64BinaryField(required=False, allow_null=True)

    class Meta:
        model = GenPerson
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'father_name', 'gender', 'national_code', 'nidentity',
            'person_image', 'thumbnail_image', 'birth_date', 'tel', 'mobile', 'email', 'education', 'job',
            'has_insurance', 'insurance_no', 'ins_start_date', 'ins_end_date', 'address', 'has_parrent',
            'team_name', 'shift', 'user', 'creation_datetime', 'modifier', 'modification_datetime'
        ]


class GenPersonRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenPersonRole
        fields = ['id', 'role_desc']


class GenMemberSerializer(serializers.ModelSerializer):
    face_template_1 = Base64BinaryField(required=False, allow_null=True)
    face_template_2 = Base64BinaryField(required=False, allow_null=True)
    face_template_3 = Base64BinaryField(required=False, allow_null=True)
    face_template_4 = Base64BinaryField(required=False, allow_null=True)
    face_template_5 = Base64BinaryField(required=False, allow_null=True)
    minutiae = Base64BinaryField(required=False, allow_null=True)
    minutiae2 = Base64BinaryField(required=False, allow_null=True)
    minutiae3 = Base64BinaryField(required=False, allow_null=True)
    section_left = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = GenMember
        fields = [
            'id', 'card_no', 'person', 'role', 'user', 'shift', 'is_black_list', 'box_radif_no', 'has_finger',
            'membership_datetime', 'modifier', 'modification_datetime', 'is_family', 'max_debit',
            'minutiae', 'minutiae2', 'minutiae3', 'salary', 'couch_id',
            'face_template_1', 'face_template_2', 'face_template_3', 'face_template_4', 'face_template_5',
            'section_left'
        ]



class GenMembershipTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenMembershipType
        fields = ['id', 'membership_type_desc']
