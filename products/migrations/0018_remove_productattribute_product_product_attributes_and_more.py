# Generated by Django 4.2 on 2023-09-15 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0017_remove_product_attributes_productattribute_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="productattribute",
            name="product",
        ),
        migrations.AddField(
            model_name="product",
            name="attributes",
            field=models.TextField(default=1),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name="AttributeOption",
        ),
        migrations.DeleteModel(
            name="ProductAttribute",
        ),
    ]
