from django.db import models
from django.core.exceptions import ValidationError
from apps.user.models import Base, User
from apps.admin.models import Category, Admin
import uuid


def generate_ticket_number():
    return f"TKT-{uuid.uuid4().hex[:8].upper()}"


class Ticket(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="tickets")
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="tickets"
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ("open", "Open"),
            ("waiting_admin", "Waiting Admin"),
            ("waiting_user", "Waiting User"),
            ("in_progress", "In Progress"),
            ("replied", "Replied"),
            ("escalated", "Escalated"),
            ("expired", "Expired"),
            ("closed", "Closed"),
        ],
        default="open",
    )
    description = models.TextField()
    priority = models.CharField(
        max_length=50,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
        default="medium",
    )
    assigned_admin = models.ForeignKey(
        Admin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    close_at = models.DateTimeField(null=True, blank=True)
    ticket_number = models.CharField(max_length=20, unique=True,
                                     default=generate_ticket_number)
    close_reason = models.TextField(null=True, blank=True)
    closed_by = models.ForeignKey(
        Admin,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="closed_tickets",
    )

    def clean(self):
        if self.status != "closed":
            exists = (
                Ticket.objects.filter(
                    user=self.user, status__in=["open", "waiting_admin",
                                                "in_progress"]
                )
                .exclude(id=self.id)
                .exists()
            )
            if exists:
                raise ValidationError(
                    "Bu userda allaqachon ochiq ticket mavjud")

    def __str__(self):
        return f"{self.ticket_number} - {self.title}"


class Message(Base):
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="messages"
    )
    sender_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sent_messages",
    )
    sender_admin = models.ForeignKey(
        Admin,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sent_messages",
    )
    content_type = models.CharField(
        max_length=50,
        choices=[
            ("text", "Text"),
            ("image", "Image"),
            ("file", "File"),
            ("video", "Video"),
            ("audio", "Audio"),
            ("location", "Location"),
        ],
        default="text",
    )
    content = models.TextField(null=True, blank=True)
    file = models.CharField(max_length=255, null=True, blank=True, help_text="Telegram file_id")
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.sender_user and not self.sender_admin:
            raise ValidationError(
                "Message sender must be either a user or an admin.")
        if self.sender_user and self.sender_admin:
            raise ValidationError(
                "Message cannot have both user and admin as sender.")

    def __str__(self):
        sender = self.sender_user or self.sender_admin
        return f"Message from {sender} on {self.timestamp}"


class AdminActivityLog(Base):
    ACTION_CHOICES = (
        ("assigned", "Assigned"),
        ("replied", "Replied"),
        ("closed", "Closed"),
        ("transferred", "Transferred"),
    )

    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    def __str__(self):
        return f"{self.admin} → {self.action}"
