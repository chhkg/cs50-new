# Generated by Django 3.2 on 2021-06-05 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_auto_20210420_2314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='image',
            field=models.URLField(default='https://nayemdevs.com/wp-content/uploads/2020/03/default-product-image.png', max_length=250),
        ),
    ]
