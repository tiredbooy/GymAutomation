import json
import pyodbc
import io
import base64
from PIL import Image
import pillow_avif  # Ensure pillow-avif-plugin is installed

from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from UserModule.models import GenMembershipType, GenPersonRole, GenShift, SecUser, GenPerson, GenMember


def convert_hex_jpeg_to_avif(hex_str):
    if not hex_str:
        return None

    try:
        # If the input is already bytes (e.g. from pyodbc VARBINARY), use it directly
        if isinstance(hex_str, bytes):
            img_bytes = hex_str
        elif isinstance(hex_str, str):
            img_bytes = bytes.fromhex(hex_str[2:] if hex_str.startswith("0x") else hex_str)
        else:
            return None  # Unsupported type

        # Load and convert the image
        image = Image.open(io.BytesIO(img_bytes))
        avif_buffer = io.BytesIO()
        image.save(avif_buffer, format="AVIF")
        return avif_buffer.getvalue()

    except Exception as e:
        print(f"Image conversion error: {e}")
        return None



class DataImportFromJsonConfigAPIView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            server = data.get('SERVER')
            database = data.get('DATABASE')

            if not server or not database:
                return JsonResponse({"error": "SERVER and DATABASE must be provided"}, status=400)

            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                "Trusted_Connection=yes;"
            )
            cursor = conn.cursor()

            # Import GenShift
            cursor.execute("SELECT ShiftID, ShiftDesc FROM Gen_Shift")
            for row in cursor.fetchall():
                GenShift.objects.update_or_create(
                    shift_id=row.ShiftID,
                    defaults={'shift_desc': row.ShiftDesc}
                )

            # Import GenPersonRole
            cursor.execute("SELECT RoleID, RoleDesc FROM Gen_PersonRole")
            for row in cursor.fetchall():
                GenPersonRole.objects.update_or_create(
                    role_id=row.RoleID,
                    defaults={'role_desc': row.RoleDesc}
                )

            # Import GenMembershipType
            cursor.execute("SELECT MembershipTypeID, MembershipTypeDesc FROM Gen_MembershipType")
            for row in cursor.fetchall():
                GenMembershipType.objects.update_or_create(
                    membership_type_id=row.MembershipTypeID,
                    defaults={'membership_type_desc': row.MembershipTypeDesc}
                )

            # Import SecUser
            cursor.execute("""
                SELECT UserID, PersonID, UserName, UPassword, IsAdmin, ShiftID, 
                IsActive, CreationDate, CreationTime
                FROM Sec_Users
            """)
            for row in cursor.fetchall():
                creation_datetime = f"{row.CreationDate} {row.CreationTime}" if row.CreationDate and row.CreationTime else None

                SecUser.objects.update_or_create(
                    user_id=row.UserID,
                    defaults={
                        'username': row.UserName,
                        'password': row.UPassword,
                        'is_admin': row.IsAdmin,
                        'shift_id': row.ShiftID,
                        'is_active': row.IsActive,
                        'creation_datetime': creation_datetime,
                        'person_id': row.PersonID,
                    }
                )

            # Import GenPerson with AVIF conversion
            cursor.execute("""
                SELECT PersonID, FirstName, LastName, FullName, FatherName, Gender, NationalCode, 
                Nidentity, PersonImage, ThumbnailImage, BirthDate, Tel, Mobile, Email, 
                Education, Job, HasInsurance, InsuranceNo, InsStartDate, InsEndDate, PAddress, 
                HasParrent, TeamName, ShiftID, UserID, CreationDate, CreationTime, Modifier, ModificationTime
                FROM Gen_Person
            """)
            for row in cursor.fetchall():
                gender = {0: 'F', 1: 'M'}.get(row.Gender, 'O')
                creation_datetime = f"{row.CreationDate} {row.CreationTime}" if row.CreationDate and row.CreationTime else None
                modification_datetime = f"{row.ModificationTime}" if row.ModificationTime else None

                person_image_avif = convert_hex_jpeg_to_avif(row.PersonImage)
                thumbnail_image_avif = convert_hex_jpeg_to_avif(row.ThumbnailImage)

                GenPerson.objects.update_or_create(
                    person_id=row.PersonID,
                    defaults={
                        'first_name': row.FirstName,
                        'last_name': row.LastName,
                        'full_name': row.FullName,
                        'father_name': row.FatherName,
                        'gender': gender,
                        'national_code': row.NationalCode,
                        'nidentity': row.Nidentity,
                        'person_image': person_image_avif,
                        'thumbnail_image': thumbnail_image_avif,
                        'birth_date': row.BirthDate,
                        'tel': row.Tel,
                        'mobile': row.Mobile,
                        'email': row.Email,
                        'education': row.Education,
                        'job': row.Job,
                        'has_insurance': row.HasInsurance,
                        'insurance_no': row.InsuranceNo,
                        'ins_start_date': row.InsStartDate,
                        'ins_end_date': row.InsEndDate,
                        'address': row.PAddress,
                        'has_parrent': row.HasParrent,
                        'team_name': row.TeamName,
                        'shift_id': row.ShiftID,
                        'user_id': row.UserID,
                        'creation_datetime': creation_datetime,
                        'modifier': row.Modifier,
                        'modification_datetime': modification_datetime,
                    }
                )

            # Import GenMember
            cursor.execute("""
                SELECT MemberID, CardNo, PersonID, RoleID, UserID, ShiftID, 
                       IsBlackList, BoxRadifNo, HasFinger, MembershipDate, MembershipTime, 
                       Modifier, Modificationtime, IsFamily, MaxDebit, Minutiae, 
                       Minutiae2, Minutiae3, Salary, FaceTmpl1, FaceTmpl2, FaceTmpl3, 
                       FaceTmpl4, FaceTmpl5
                FROM Gen_Members
            """)
            for row in cursor.fetchall():
                membership_datetime = f"{row.MembershipDate} {row.MembershipTime}" if row.MembershipDate and row.MembershipTime else None
                modification_datetime = f"{row.Modificationtime}" if row.Modificationtime else None

                role_instance = GenPersonRole.objects.get(role_id=row.RoleID)
                user_instance = SecUser.objects.get(user_id=row.UserID)
                shift_instance = GenShift.objects.get(shift_id=row.ShiftID)

                GenMember.objects.update_or_create(
                    member_id=row.MemberID,
                    defaults={
                        'card_no': row.CardNo,
                        'person_id': row.PersonID,
                        'role_id': role_instance,
                        'user_id': user_instance.user_id,
                        'shift_id': shift_instance.shift_id,
                        'is_black_list': row.IsBlackList,
                        'box_radif_no': row.BoxRadifNo,
                        'has_finger': row.HasFinger,
                        'membership_datetime': membership_datetime,
                        'modifier': row.Modifier,
                        'modification_datetime': modification_datetime,
                        'is_family': row.IsFamily,
                        'max_debit': row.MaxDebit,
                        'minutiae': row.Minutiae,
                        'minutiae2': row.Minutiae2,
                        'minutiae3': row.Minutiae3,
                        'salary': row.Salary,
                        'face_template_1': row.FaceTmpl1,
                        'face_template_2': row.FaceTmpl2,
                        'face_template_3': row.FaceTmpl3,
                        'face_template_4': row.FaceTmpl4,
                        'face_template_5': row.FaceTmpl5,
                    }
                )

            conn.close()
            return Response({"message": "✅ Data imported successfully."})

        except Exception as e:
            return Response({"error": f"❌ Import failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
