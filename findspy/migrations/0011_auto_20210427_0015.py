# Generated by Django 3.1.6 on 2021-04-27 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('findspy', '0010_auto_20210426_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='playerTurn',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]