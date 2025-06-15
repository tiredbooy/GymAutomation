from django.db import models

class GenShift(models.Model):
    id = models.BigIntegerField(primary_key=True)
    shift_desc = models.CharField(max_length=255)

    def __str__(self):
        return f"Shift {self.id}: {self.shift_desc}"

class GenPersonRole(models.Model):
    id = models.BigIntegerField(primary_key=True)
    role_desc = models.CharField(max_length=255)

    def __str__(self):
        return self.role_desc

class GenMembershipType(models.Model):
    id = models.BigIntegerField(primary_key=True)
    membership_type_desc = models.CharField(max_length=255)

    def __str__(self):
        return self.membership_type_desc

class SecUser(models.Model):
    id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey('GenPerson', null=True, blank=True, on_delete=models.SET_NULL, related_name='users')
    username = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    shift = models.ForeignKey(GenShift, null=True, blank=True, on_delete=models.SET_NULL, related_name='users')
    is_active = models.BooleanField(default=True)
    creation_datetime = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    def __str__(self):
        return self.username or f"User {self.id}"

class GenPerson(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=510, null=True, blank=True)
    father_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    national_code = models.CharField(max_length=50, null=True, blank=True)
    nidentity = models.CharField(max_length=50, null=True, blank=True)
    person_image = models.BinaryField(null=True, blank=True)
    thumbnail_image = models.BinaryField(null=True, blank=True)
    birth_date = models.CharField(max_length=510, null=True, blank=True)
    tel = models.CharField(max_length=50, null=True, blank=True)
    mobile = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    education = models.CharField(max_length=255, null=True, blank=True)
    job = models.CharField(max_length=255, null=True, blank=True)
    has_insurance = models.BooleanField(null=True, default=False)
    insurance_no = models.CharField(max_length=50, null=True, blank=True)
    ins_start_date = models.CharField(max_length=510, null=True, blank=True)
    ins_end_date = models.CharField(max_length=510, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    has_parrent = models.BooleanField(default=False)
    team_name = models.CharField(max_length=255, null=True, blank=True)
    shift = models.ForeignKey('GenShift', null=True, blank=True, on_delete=models.SET_NULL, related_name='people')
    user = models.ForeignKey('SecUser', null=True, blank=True, on_delete=models.SET_NULL, related_name='people_created')
    creation_datetime = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    modifier = models.CharField(max_length=255, null=True, blank=True)
    modification_datetime = models.CharField(max_length=510, null=True, blank=True)

    def __str__(self):
        return self.full_name or f"Person {self.id}"

class GenMember(models.Model):
    id = models.BigIntegerField(primary_key=True)
    card_no = models.CharField(max_length=50, null=True, blank=True)
    couch_id = models.IntegerField(null=True, blank=True)
    person = models.ForeignKey(GenPerson, null=True, blank=True, on_delete=models.SET_NULL, related_name='members')
    role = models.ForeignKey(GenPersonRole, null=True, blank=True, on_delete=models.SET_NULL, related_name='members')
    user = models.ForeignKey(SecUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='members_added')
    shift = models.ForeignKey(GenShift, null=True, blank=True, on_delete=models.SET_NULL, related_name='members')
    is_black_list = models.BooleanField(default=False)
    box_radif_no = models.CharField(max_length=50, null=True, blank=True)
    has_finger = models.BooleanField(default=True, null=True, blank=True)
    membership_datetime = models.CharField(max_length=255, null=True, blank=True)
    modifier = models.CharField(max_length=255, null=True, blank=True)
    modification_datetime = models.CharField(max_length=255, null=True, blank=True)
    is_family = models.BooleanField(default=False, null=True, blank=True)
    max_debit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    minutiae = models.BinaryField(null=True, blank=True)
    minutiae2 = models.BinaryField(null=True, blank=True)
    minutiae3 = models.BinaryField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    face_template_1 = models.BinaryField(null=True, blank=True)
    face_template_2 = models.BinaryField(null=True, blank=True)
    face_template_3 = models.BinaryField(null=True, blank=True)
    face_template_4 = models.BinaryField(null=True, blank=True)
    face_template_5 = models.BinaryField(null=True, blank=True)
    creation_datetime = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    section_left = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Member {self.id} - {self.card_no}"