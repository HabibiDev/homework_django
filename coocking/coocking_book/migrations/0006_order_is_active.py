# Generated by Django 2.1.5 on 2019-02-16 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coocking_book', '0005_auto_20190214_2258'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]