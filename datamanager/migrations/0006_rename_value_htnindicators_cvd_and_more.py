# Generated by Django 4.2.10 on 2024-02-28 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamanager', '0005_htnindicators'),
    ]

    operations = [
        migrations.RenameField(
            model_name='htnindicators',
            old_name='value',
            new_name='cvd',
        ),
        migrations.AddField(
            model_name='htnindicators',
            name='high_risk',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='htnindicators',
            name='low_risk',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='htnindicators',
            name='measurements',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]
