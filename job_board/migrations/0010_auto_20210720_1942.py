# Generated by Django 3.2.5 on 2021-07-20 13:42

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('job_board', '0009_jobadditionalfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidatejob',
            name='mcq_exam_started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='candidatejob',
            name='step',
            field=models.IntegerField(default=0, max_length=11),
        ),
        migrations.AlterField(
            model_name='job',
            name='additional_requirement',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='compensation',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='educational_requirement',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_context',
            field=tinymce.models.HTMLField(max_length=500),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_description',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_responsibility',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
    ]
