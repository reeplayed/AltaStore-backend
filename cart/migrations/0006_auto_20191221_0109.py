# Generated by Django 2.2.3 on 2019-12-21 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0005_auto_20191220_0515'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cart',
            options={},
        ),
        migrations.AddField(
            model_name='item',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True),
        ),
    ]
