# Generated by Django 4.2.10 on 2024-02-29 08:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datamanager', '0010_alter_htnindicators_high_risk_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='htnindicators',
            old_name='created_at',
            new_name='visit_date',
        ),
    ]
