# Generated by Django 5.0.6 on 2024-05-29 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_issue'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='title',
            field=models.CharField(default='Default Title', max_length=200),
        ),
    ]
