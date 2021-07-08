# Generated by Django 3.2.1 on 2021-05-25 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0007_auto_20210509_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='character',
            name='texture',
            field=models.TextField(default='default'),
        ),
        migrations.AlterField(
            model_name='character',
            name='agility',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='character',
            name='attack',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='character',
            name='charisma',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='character',
            name='defense',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='character',
            name='magick',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='character',
            name='stamina',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='character',
            name='strength',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='character',
            name='vitality',
            field=models.IntegerField(default=1),
        ),
    ]
