# Generated by Django 4.2.16 on 2024-12-15 05:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0006_alter_openinghour_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='openinghour',
            options={'ordering': ('day', '-from_hour')},
        ),
    ]
