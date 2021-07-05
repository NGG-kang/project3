# Generated by Django 3.2.3 on 2021-07-03 01:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('search_app', '0004_auto_20210701_2146'),
    ]

    operations = [
        migrations.AddField(
            model_name='myenterprise',
            name='link',
            field=models.SlugField(blank=True, max_length=1000),
        ),
        migrations.AddField(
            model_name='myenterprise',
            name='photo',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, to='search_app.enterphoto'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='myenterprise',
            name='name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
