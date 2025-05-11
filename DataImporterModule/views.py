import json
import pyodbc
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from UserModule.models import GenMembershipType, GenPersonRole, GenShift, SecUser, GenPerson, GenMember
import os
from datetime import datetime
from django.http import JsonResponse, FileResponse, HttpResponseServerError, HttpResponseBadRequest
from django.conf import settings
import subprocess
from rest_framework.views import APIView
from django.core.management import call_command
from rest_framework.decorators import api_view

class DataImportFromJsonConfigAPIView(APIView):
    def post(self, request):
        try:
            # Step 1: Parse the request  data to get server and database info
            data = json.loads(request.body)
            server = data.get('SERVER')
            database = data.get('DATABASE')

            if not server or not database:
                return JsonResponse({"error": "SERVER and DATABASE must be provided"}, status=400)

            # Step 2: Connect to the SQL Server using pyodbc
            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                "Trusted_Connection=yes;"
            )
            cursor = conn.cursor()

            # Step 3: Import data into Django models

            # Load GenShift (all rows)
            cursor.execute("SELECT ShiftID, ShiftDesc FROM Gen_Shift")
            for row in cursor.fetchall():
                GenShift.objects.update_or_create(
                    shift_id=row.ShiftID,
                    defaults={'shift_desc': row.ShiftDesc}
                )

            # Load GenPersonRole (all rows)
            cursor.execute("SELECT RoleID, RoleDesc FROM Gen_PersonRole")
            for row in cursor.fetchall():
                GenPersonRole.objects.update_or_create(
                    role_id=row.RoleID,
                    defaults={'role_desc': row.RoleDesc}
                )

            # Load GenMembershipType (all rows)
            cursor.execute("SELECT MembershipTypeID, MembershipTypeDesc FROM Gen_MembershipType")
            for row in cursor.fetchall():
                GenMembershipType.objects.update_or_create(
                    membership_type_id=row.MembershipTypeID,
                    defaults={'membership_type_desc': row.MembershipTypeDesc}
                )

            # Load SecUser (all rows)
            cursor.execute("""
                SELECT UserID, PersonID, UserName, UPassword, IsAdmin, ShiftID, 
                IsActive, CreationDate, CreationTime
                FROM Sec_Users
            """)
            for row in cursor.fetchall():
                # We no longer parse datetime, just store it as a string
                creation_datetime = f"{row.CreationDate} {row.CreationTime}" if row.CreationDate and row.CreationTime else None

                # Update or create the SecUser
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

            # Load GenPerson (all rows)
            cursor.execute("""
                SELECT PersonID, FirstName, LastName, FullName, FatherName, Gender, NationalCode, 
                Nidentity, PersonImage, ThumbnailImage, BirthDate, Tel, Mobile, Email, 
                Education, Job, HasInsurance, InsuranceNo, InsStartDate, InsEndDate, PAddress, 
                HasParrent, TeamName, ShiftID, UserID, CreationDate, CreationTime, Modifier, ModificationTime
                FROM Gen_Person
            """)
            for row in cursor.fetchall():
                # Convert Gender field
                if row.Gender == 0:
                    gender = 'F'  # Female
                elif row.Gender == 1:
                    gender = 'M'  # Male
                else:
                    gender = 'O'  # Other

                # Handle date/time as strings, no parsing
                creation_datetime = f"{row.CreationDate} {row.CreationTime}" if row.CreationDate and row.CreationTime else None
                modification_datetime = f"{row.ModificationTime}" if row.ModificationTime else None

                # Update or create the GenPerson
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
                        'person_image': row.PersonImage,
                        'thumbnail_image': row.ThumbnailImage,
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

            # Load GenMember (all rows)
            cursor.execute("""
                SELECT [MemberID], [CardNo], [PersonID], [RoleID], [UserID], [ShiftID], 
                       [IsBlackList], [BoxRadifNo], [HasFinger], [MembershipDate], [MembershipTime], 
                       [Modifier], [Modificationtime], [IsFamily], [MaxDebit], [Minutiae], 
                       [Minutiae2], [Minutiae3], [Salary], [FaceTmpl1], [FaceTmpl2], [FaceTmpl3], 
                       [FaceTmpl4], [FaceTmpl5]
                FROM [Gen_Members]
            """)
            for row in cursor.fetchall():
                # Format Membership Date and Time to String
                membership_datetime = f"{row.MembershipDate} {row.MembershipTime}" if row.MembershipDate and row.MembershipTime else None
                modification_datetime = f"{row.Modificationtime}" if row.Modificationtime else None

                # Get instances of related models
                role_instance = GenPersonRole.objects.get(role_id=row.RoleID)
                user_instance = SecUser.objects.get(user_id=row.UserID)
                shift_instance = GenShift.objects.get(shift_id=row.ShiftID)

                # Update or create the GenMember
                GenMember.objects.update_or_create(
                    member_id=row.MemberID,
                    defaults={
                        'card_no': row.CardNo,
                        'person_id': row.PersonID,
                        'role_id': role_instance,  # Use the actual instance here
                        'user_id': user_instance.user_id,  # Pass the user_id (not the whole instance)
                        'shift_id': shift_instance.shift_id,  # Pass the shift_id (not the whole instance)
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

            # Close the connection
            conn.close()

            return Response({"message": "✅ Data imported successfully."})

        except Exception as e:
            return Response({"error": f"❌ Import failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

