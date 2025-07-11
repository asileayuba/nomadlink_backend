# Generated by Django 5.2.3 on 2025-07-06 13:50

import cloudinary.models
import kyc.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kyc', '0003_kyc_id_document_file_size_kyc_id_document_file_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kyc',
            name='id_document_file_size',
        ),
        migrations.RemoveField(
            model_name='kyc',
            name='id_document_file_type',
        ),
        migrations.RemoveField(
            model_name='kyc',
            name='id_type',
        ),
        migrations.AlterField(
            model_name='kyc',
            name='id_document',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, validators=[kyc.models.validate_file_pdf_only]),
        ),
    ]
