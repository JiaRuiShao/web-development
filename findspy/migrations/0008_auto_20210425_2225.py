# Generated by Django 3.1.6 on 2021-04-26 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('findspy', '0007_auto_20210425_2156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='phase',
            field=models.CharField(blank=None, default='', max_length=100, null=None),
        ),
    ]
