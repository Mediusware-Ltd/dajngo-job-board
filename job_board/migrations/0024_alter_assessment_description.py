# Generated by Django 3.2.5 on 2021-07-25 11:04

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('job_board', '0023_assessment_pass_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='description',
            field=tinymce.models.HTMLField(),
        ),
    ]
