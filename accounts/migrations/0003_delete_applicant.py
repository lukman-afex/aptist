# Generated by Django 4.1 on 2022-08-27 12:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0002_alter_result_applicants'),
        ('accounts', '0002_alter_organization_slug'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Applicant',
        ),
    ]
