# Generated by Django 4.0.2 on 2022-02-15 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_profile_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='code',
            field=models.IntegerField(default=96168177),
        ),
    ]
