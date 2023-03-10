# Generated by Django 4.1.7 on 2023-02-19 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='food_type',
        ),
        migrations.RemoveField(
            model_name='item',
            name='section',
        ),
        migrations.RemoveField(
            model_name='item',
            name='type',
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('Waiting', 'Waiting'), ('Delivered', 'Delivered'), ('Paid', 'Paid')], max_length=10),
        ),
        migrations.DeleteModel(
            name='FoodType',
        ),
        migrations.DeleteModel(
            name='ItemType',
        ),
        migrations.DeleteModel(
            name='Section',
        ),
    ]