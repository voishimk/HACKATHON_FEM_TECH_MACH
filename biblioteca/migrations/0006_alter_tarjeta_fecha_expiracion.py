# Generated by Django 4.2.3 on 2024-04-20 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioteca', '0005_tarjeta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarjeta',
            name='fecha_expiracion',
            field=models.CharField(max_length=5),
        ),
    ]
