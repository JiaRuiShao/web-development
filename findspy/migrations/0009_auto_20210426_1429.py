# Generated by Django 3.1.6 on 2021-04-26 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('findspy', '0008_auto_20210425_2225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='msg',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='winner',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
    ]
