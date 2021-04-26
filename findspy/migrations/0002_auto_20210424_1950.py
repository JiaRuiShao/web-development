# Generated by Django 3.1.6 on 2021-04-24 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('findspy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='vote',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='room',
            name='game_end',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='room',
            name='msg',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='room',
            name='winner',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
    ]
