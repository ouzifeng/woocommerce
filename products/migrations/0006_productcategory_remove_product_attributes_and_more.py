# Generated by Django 4.2 on 2023-09-14 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0005_productmetadata"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name="product",
            name="attributes",
        ),
        migrations.RemoveField(
            model_name="product",
            name="categories",
        ),
        migrations.CreateModel(
            name="ProductAttribute",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("key", models.CharField(max_length=255)),
                ("value", models.TextField()),
            ],
            options={
                "unique_together": {("key", "value")},
            },
        ),
        migrations.AddField(
            model_name="product",
            name="attributes",
            field=models.ManyToManyField(
                related_name="products", to="products.productattribute"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="categories",
            field=models.ManyToManyField(
                related_name="products", to="products.productcategory"
            ),
        ),
    ]