# Generated by Django 2.2.3 on 2020-02-18 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20200218_1931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_image',
            field=models.ImageField(default='wiedzmin.jpeg', upload_to='profile_images/'),
        ),
    ]
