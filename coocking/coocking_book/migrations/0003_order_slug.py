# Generated by Django 2.1.7 on 2019-02-23 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coocking_book', '0002_auto_20190223_0732'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True),
        ),
    ]
