from django.db import models


# Create your models here.

class Contact(models.Model):
    class Meta:
        db_table = 'contact'

    name = models.CharField(max_length=100, null=True, blank=True)
    surname = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=100, null=True, blank=True)
    note = models.TextField()

    def __str__(self):
        return f'{self.name} {self.surname} {self.email}'
