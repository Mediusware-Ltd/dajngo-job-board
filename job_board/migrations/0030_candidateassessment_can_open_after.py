# Generated by Django 3.2.5 on 2021-07-28 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_board', '0029_rename_pass_score_assessment_pass_percentage'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateassessment',
            name='can_open_after',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]