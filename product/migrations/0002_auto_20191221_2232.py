# Generated by Django 2.2.3 on 2019-12-21 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='brand',
        ),
        migrations.RemoveField(
            model_name='product',
            name='quantity',
        ),
        migrations.AddField(
            model_name='product',
            name='cloth',
            field=models.CharField(blank=True, choices=[('white', 'White'), ('green', 'Green'), ('black', 'Black'), ('grey', 'Grey'), ('other', 'Other')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.CharField(blank=True, choices=[('white', 'White'), ('green', 'Green'), ('black', 'Black'), ('grey', 'Grey'), ('other', 'Other')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(blank=True, choices=[('narozniki', 'Narożniki'), ('sofy', 'Sofy'), ('fotele', 'Fotele')], max_length=50, null=True),
        ),
    ]
