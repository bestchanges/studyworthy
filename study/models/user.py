from django.db import models
from .abstract_user import AbstractUser


class User(AbstractUser):
    google_account = models.CharField(max_length=30)
    github_account = models.CharField(max_length=30)

