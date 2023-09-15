# Generated by Django 4.2 on 2023-09-13 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0003_alter_product_slug"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="id",
        ),
        migrations.AlterField(
            model_name="product",
            name="product_id",
            field=models.IntegerField(primary_key=True, serialize=False, unique=True),
        ),
    ]