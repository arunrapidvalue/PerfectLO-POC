# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-02-05 09:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_questionnaires', '0002_auto_20180202_0514'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questionnaire',
            old_name='question_uuid',
            new_name='questionnaire_uuid',
        ),
    ]
