# Generated by Django 4.2.10 on 2024-02-28 09:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datamanager', '0009_remove_htnindicators_low_risk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='htnindicators',
            name='high_risk',
            field=models.BooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='htnindicators',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='htn_indicators', to='datamanager.patients'),
        ),
    ]