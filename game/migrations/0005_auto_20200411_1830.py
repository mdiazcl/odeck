# Generated by Django 3.0 on 2020-04-11 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_game_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='graveyard_position',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
