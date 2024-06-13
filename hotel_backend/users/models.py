from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
gender_choices = (
    ('male', 'male'),
    ('female', 'female'),
    ('other', 'other'),
)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    fathers_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    birthday = models.DateField(blank=True, null=True)
    birthplace = models.CharField(max_length=100, blank=True, null=True)
    USERNAME_FIELD = 'email'
    personal_number = models.CharField(max_length=100)
    gender = models.CharField(choices=gender_choices, max_length=50)
    phone_number = models.CharField(max_length=50)
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'personal_number', 'gender', 'phone_number']

    def __str__(self):
        return f'{self.pk} {self.first_name} {self.last_name}'

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'user'
        verbose_name_plural = 'users'


class AdditionalInformation(models.Model):
    class Meta:
        abstract = True

    resume = models.FileField(upload_to='employee/documents/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='employee/images/', blank=True, null=True)


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin')

    class Meta:
        db_table = 'hotel_admin'


class HotelManager(AdditionalInformation):
    class Meta:
        db_table = 'hotel_manager'

    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Cleaner(AdditionalInformation):
    class Meta:
        db_table = 'cleaner'

    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Guest(models.Model):
    class Meta:
        db_table = 'hotel_guest'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='guest/images/', blank=True, null=True)

    def __str__(self):
        return str(self.user)

class Receptionist(AdditionalInformation):
    class Meta:
        db_table = 'receptionist'

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

class Accountant(AdditionalInformation):
    class Meta:
        db_table = 'accountant'

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)