# Generated by Django 4.2.22 on 2025-06-26 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casting', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='casting',
            name='cash_received',
            field=models.CharField(blank=True, default='0', max_length=158, null=True),
        ),
        migrations.AlterField(
            model_name='casting',
            name='converted24k',
            field=models.CharField(blank=True, default='0', max_length=158, null=True),
        ),
        migrations.AlterField(
            model_name='casting',
            name='gold_received',
            field=models.CharField(blank=True, default='0', max_length=158, null=True),
        ),
        migrations.AlterField(
            model_name='casting',
            name='service_charges_amount',
            field=models.CharField(blank=True, default='0', max_length=158, null=True),
        ),
        migrations.AlterField(
            model_name='casting',
            name='service_charges_rate',
            field=models.CharField(blank=True, default='0', max_length=158, null=True),
        ),
        migrations.AlterField(
            model_name='casting',
            name='total_weight24k',
            field=models.CharField(blank=True, default='0', max_length=158, null=True),
        ),
        migrations.AlterField(
            model_name='casting',
            name='wastage_percentage',
            field=models.CharField(blank=True, default='0', max_length=158, null=True),
        ),
        migrations.AlterField(
            model_name='casting',
            name='wastage_weight',
            field=models.CharField(blank=True, default='0', max_length=158, null=True),
        ),
        migrations.AlterField(
            model_name='casting',
            name='weight',
            field=models.CharField(blank=True, default='0', max_length=158, null=True),
        ),
        migrations.AlterField(
            model_name='flask',
            name='input_weight',
            field=models.CharField(blank=True, default='0', max_length=158, null=True),
        ),
        migrations.AlterField(
            model_name='flask',
            name='machine_wastage',
            field=models.CharField(blank=True, default='0', max_length=158, null=True),
        ),
        migrations.AlterField(
            model_name='flask',
            name='output_weight',
            field=models.CharField(blank=True, default='0', max_length=158, null=True),
        ),
        migrations.AlterField(
            model_name='flask',
            name='production_weight',
            field=models.CharField(blank=True, default='0', max_length=158, null=True),
        ),
    ]
