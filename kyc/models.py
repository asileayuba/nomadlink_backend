from django.db import models
from accounts.models import CustomUser
from django.core.exceptions import ValidationError
import os

# PDF validator
def validate_file_pdf_only(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError("Only PDF files are allowed.")

    if file.size > 4 * 1024 * 1024:  # 4MB
        raise ValidationError("File size must be under 4MB.")

# Image validator
def validate_image_size(file):
    if file.size > 4 * 1024 * 1024:  # 4MB
        raise ValidationError("Image file size must be under 4MB.")

class KYC(models.Model):
    LEVEL_CHOICES = (
        ('level_1', 'Level 1'),
        ('level_2', 'Level 2'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    ID_TYPE_CHOICES = (
        ('passport', 'Passport'),
        ('national_id', 'National ID'),
        ('driver_license', 'Driver’s License'),
        ('other', 'Other'),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='kyc')
    full_name = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    id_type = models.CharField(max_length=50, choices=ID_TYPE_CHOICES, default='passport')
    id_document = models.FileField(
        upload_to='kyc/documents/',
        blank=True,
        null=True,
        validators=[validate_file_pdf_only]
    )
    id_document_file_type = models.CharField(max_length=50, blank=True, null=True)
    id_document_file_size = models.PositiveIntegerField(blank=True, null=True)

    selfie_photo = models.ImageField(
        upload_to='kyc/selfies/',
        blank=True,
        null=True,
        validators=[validate_image_size]
    )
    selfie_file_type = models.CharField(max_length=50, blank=True, null=True)
    selfie_file_size = models.PositiveIntegerField(blank=True, null=True)

    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='level_1')
    review_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_verified = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Track file metadata
        if self.id_document:
            self.id_document_file_type = os.path.splitext(self.id_document.name)[1].lower()
            self.id_document_file_size = self.id_document.size

        if self.selfie_photo:
            self.selfie_file_type = os.path.splitext(self.selfie_photo.name)[1].lower()
            self.selfie_file_size = self.selfie_photo.size

        # Auto-promote to Level 2 if both files are present
        if self.id_document and self.selfie_photo:
            self.level = 'level_2'
        else:
            self.level = 'level_1'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.level} - {self.review_status}"
