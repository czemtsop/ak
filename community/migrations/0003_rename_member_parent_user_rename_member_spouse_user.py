# Generated by Django 5.2.4 on 2025-07-10 03:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0002_parent_spouse'),
    ]

    operations = [
        migrations.RenameField(
            model_name='parent',
            old_name='member',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='spouse',
            old_name='member',
            new_name='user',
        ),
    ]
