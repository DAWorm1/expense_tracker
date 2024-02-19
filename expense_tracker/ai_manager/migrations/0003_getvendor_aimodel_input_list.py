# Generated by Django 5.0.1 on 2024-02-18 20:05

import ai_manager.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_manager', '0002_alter_getvendor_aimodel_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='getvendor_aimodel',
            name='input_list',
            field=models.TextField(blank=True, default='', validators=[ai_manager.validators.CSV_Validator]),
        ),
    ]
