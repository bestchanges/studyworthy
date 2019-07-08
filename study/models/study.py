from django.db import models


class Study(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In progress'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled')
    ]

    # ToDo Uncomment after Course Model is merged in
    # course = models.OneToOneField(Course, on_delete=models.CASCADE)
    started_at = models.DateField()
    status = models.CharField(max_length=11, choices=STATUS_CHOICES)

