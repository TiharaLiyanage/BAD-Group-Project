# Generated by Django 5.1.3 on 2025-04-21 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_alter_menuitem_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="menuitem",
            name="image",
            field=models.CharField(max_length=255),
        ),
    ]
