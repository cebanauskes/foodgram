# Generated by Django 3.0.8 on 2020-09-05 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amount',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='duration',
            field=models.IntegerField(default=1),
        ),
    ]