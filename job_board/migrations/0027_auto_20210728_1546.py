# Generated by Django 3.2.5 on 2021-07-28 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_board', '0026_auto_20210727_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobsummery',
            name='salary_range',
            field=models.CharField(default=4, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='jobsummery',
            name='experience',
            field=models.CharField(max_length=255),
        ),
    ]