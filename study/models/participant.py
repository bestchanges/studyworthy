from django.db import models
from .user import User
from .study import Study


class Participant(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('trainer', 'Trainer'),
        ('admin', 'Admin')
    ]
    STATUS_CHOICES = [
        ('possible', 'Possible'),
        ('active', 'Active'),
        ('lost', 'Lost')
    ]

    class Meta:
        unique_together = [['study', 'user']]

    study = models.OneToOneField(Study, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=7, choices=ROLE_CHOICES)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    score = models.IntegerField()

    @property
    def nickname(self):
        return "%s_%s" % (self.user.first_name, self.user.last_name)
