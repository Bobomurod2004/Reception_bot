from django.db import models


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class User(Base):
    LANGUAGE_CHOICES = [
        ('uz', 'O\'zbek'),
        ('ru', 'Русский'),
        ('en', 'English'),
    ]

    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=150, null=True, blank=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,
                                default='uz')

    def __str__(self):
        return f"{self.username} ({self.telegram_id})"
