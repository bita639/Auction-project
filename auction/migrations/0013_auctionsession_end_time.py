# Generated by Django 3.0.8 on 2020-07-31 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0012_auto_20200731_2034'),
    ]

    operations = [
        migrations.AddField(
            model_name='auctionsession',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]