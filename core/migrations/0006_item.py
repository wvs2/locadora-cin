# Generated by Django 2.1.5 on 2019-01-29 01:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20190128_2036'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_serie', models.CharField(max_length=150, verbose_name='Número de Série')),
                ('data_aquisicao', models.DateField(verbose_name='Data de Aquisição')),
                ('filme', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.Filme')),
                ('tipo_midia', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.Midia')),
            ],
            options={
                'verbose_name': 'Item',
                'verbose_name_plural': 'Itens',
                'ordering': ['data_aquisicao'],
            },
        ),
    ]
