from django.db import models
from apps.user.models import User, Base


class Admin(Base):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='admin_profile')
    role = models.CharField(max_length=100, choices=ROLE_CHOICES,
                            default='admin')
    is_blocked = models.BooleanField(default=False)
    last_assigned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Admin: {self.user.username} - Role: {self.role}"

    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'


class Category(Base):
    # Multilingual name fields
    name_uz = models.CharField(max_length=100, verbose_name="Name (Uzbek)", default="Tarjima kerak")
    name_ru = models.CharField(max_length=100, verbose_name="Name (Russian)", default="Требуется перевод")
    name_en = models.CharField(max_length=100, verbose_name="Name (English)", default="Translation needed")
    
    description = models.TextField(null=True, blank=True)
    
    # Activation and ordering
    is_active = models.BooleanField(default=True, verbose_name="Active")
    order = models.PositiveIntegerField(default=0, verbose_name="Order")

    def __str__(self):
        return self.name_uz  # Default to Uzbek

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'id']


class AdminCategory(Base):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE,
                              related_name='categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='admins')

    def __str__(self):
        return f"{self.admin.user.username} - {self.category.name_uz}"

    class Meta:
        verbose_name = 'Admin Category'
        verbose_name_plural = 'Admin Categories'
        unique_together = ('admin', 'category')


class AdminActivity(Base):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE,
                              related_name='activities')
    date = models.DateTimeField(auto_now_add=True)
    assigned_tickets = models.IntegerField(default=0)
    answered_tickets = models.IntegerField(default=0)
    pending_tickets = models.IntegerField(default=0)
    avg_response_time = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.admin.user.username} - {self.date}"

    class Meta:
        verbose_name = 'Admin Activity'
        verbose_name_plural = 'Admin Activities'
