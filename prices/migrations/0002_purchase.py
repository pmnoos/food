# Generated by Django 5.1.1 on 2024-10-02 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_name', models.CharField(max_length=255)),
                ('date_of_purchase', models.DateField()),
                ('item_product', models.CharField(max_length=255)),
                ('package_unit_type', models.CharField(max_length=50)),
                ('price_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField()),
                ('total_cost', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('running_total', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
            ],
        ),
    ]
