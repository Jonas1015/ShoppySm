# Generated by Django 3.1.2 on 2021-01-24 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('istock_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
