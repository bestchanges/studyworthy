from django.db import models
from .abstract_user import AbstractUser
from .user import User


class ApplicationForm(AbstractUser):
    comment = models.TextField()
    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
