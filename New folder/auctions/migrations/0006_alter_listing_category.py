# Generated by Django 3.2 on 2021-06-05 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_listing_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(default='No Category', max_length=30),
        ),
    ]
