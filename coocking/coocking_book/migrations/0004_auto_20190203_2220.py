# Generated by Django 2.1.5 on 2019-02-03 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coocking_book', '0003_auto_20190203_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='ingredient',
            field=models.ManyToManyField(blank=True, null=True, related_name='dishes', to='coocking_book.Ingredient'),
        ),
    ]
