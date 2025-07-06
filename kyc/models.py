from django.db import models
from accounts.models import CustomUser
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField
import os

# PDF validator for Cloudinary
def validate_file_pdf_only(file):
    try:
        ext = os.path.splitext(str(file))[1].lower()
    except Exception:
        raise ValidationError("Invalid file. Could not determine extension.")

    if ext != '.pdf':
        raise ValidationError("Only PDF files are allowed.")

    # File size validation is skipped because CloudinaryField doesn't expose `.size` directly.
    # Recommend validating file size on frontend or via Cloudinary API.

# Image validator for Cloudinary
def validate_image_size(file):
    # File size not accessible reliably from CloudinaryField.
    # Add check via Cloudinary upload presets or frontend.
    pass  # Placeholder if needed later

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

    id_document = CloudinaryField(
        resource_type='raw',
        blank=True,
        null=True,
        validators=[validate_file_pdf_only]
    )
    id_document_file_type = models.CharField(max_length=50, blank=True, null=True)
    id_document_file_size = models.PositiveIntegerField(blank=True, null=True)

    selfie_photo = CloudinaryField(
        resource_type='image',
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
        # Assign file metadata if available (best-effort with CloudinaryField)
        if self.id_document:
            self.id_document_file_type = os.path.splitext(str(self.id_document))[1].lower()

        if self.selfie_photo:
            self.selfie_file_type = os.path.splitext(str(self.selfie_photo))[1].lower()

        # Auto-promote to Level 2 if both files are present
        if self.id_document and self.selfie_photo:
            self.level = 'level_2'
        else:
            self.level = 'level_1'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.level} - {self.review_status}"
