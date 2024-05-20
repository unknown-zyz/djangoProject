# Generated by Django 4.2.4 on 2024-05-19 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('DocSet', '0001_initial'),
        ('Chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='type',
            field=models.CharField(choices=[('AMM', ' '), ('FIM', ' ')], default='AMM', max_length=10),
        ),
        migrations.AlterField(
            model_name='chat',
            name='docSet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='chats', to='DocSet.docset'),
        ),
    ]