# Generated by Django 2.2.3 on 2019-07-21 16:24

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_auto_20190721_1511'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
            ],
        ),
        migrations.AlterField(
            model_name='isic',
            name='holder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='isics', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='isic',
            name='number',
            field=models.CharField(max_length=17, validators=[django.core.validators.RegexValidator(code='invalid_number', message='ISIC number must have 17 digits', regex='^[0-9]{17}$')]),
        ),
    ]
