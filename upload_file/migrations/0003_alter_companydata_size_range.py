# Generated by Django 4.2.13 on 2024-06-12 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload_file', '0002_alter_companydata_country_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companydata',
            name='size_range',
            field=models.CharField(default=None, max_length=50, null=True),
        ),
    ]