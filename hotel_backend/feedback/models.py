from django.db import models
from users.models import Guest
# Create your models here.


class Feedback(models.Model):
    class Meta:
        db_table = 'feedback'

    stars = models.IntegerField()
    text = models.TextField(null=True, blank=True)
    guest = models.ForeignKey(Guest, related_name='feedbacks', on_delete=models.CASCADE)
    date_time_created = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField(default=False)

    def __str__(self):
        return f'Feed back from {self.guest.user.email}'

