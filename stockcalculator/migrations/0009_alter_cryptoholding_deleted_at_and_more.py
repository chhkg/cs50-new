# Generated by Django 4.1.7 on 2023-04-14 08:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stockcalculator", "0008_alter_stockholding_deleted_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cryptoholding",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="fiatholding",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
