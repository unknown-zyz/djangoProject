# Generated by Django 4.2.4 on 2024-05-20 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DocSet', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='docset',
            name='amm_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='docset',
            name='fim_id',
            field=models.IntegerField(default=0),
        ),
    ]
