# Generated by Django 3.2.5 on 2021-07-20 19:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('job_board', '0013_candidateassessmentanswer'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateassessmentanswer',
            name='candidate_job',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='job_board.candidatejob'),
            preserve_default=False,
        ),
    ]
