# Generated by Django 3.1.6 on 2021-04-25 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('findspy', '0002_auto_20210424_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='voteTime',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
