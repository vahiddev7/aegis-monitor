from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower, Trim


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="email address")

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(email=Lower(Trim("email"))),
                name="users_email_normalized",
            )
        ]

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)
