# Generated by Django 3.1.2 on 2021-02-11 19:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('istock_app', '0006_auto_20210211_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='product_name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='sales',
            name='date_added',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 2, 11, 22, 39, 9, 406589), null=True),
        ),
    ]
