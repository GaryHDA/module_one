# Generated by Django 2.0.5 on 2018-07-16 00:56

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='All_Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, db_column='date', null=True)),
                ('length', models.IntegerField(db_column='length', default=0)),
                ('quantity', models.IntegerField(db_column='quantity', default=0)),
            ],
            options={
                'db_table': 'all_items',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Beaches',
            fields=[
                ('location', models.CharField(blank=True, db_column='location', max_length=100, primary_key=True, serialize=False)),
                ('latitude', models.DecimalField(blank=True, db_column='latitude', decimal_places=8, max_digits=11, null=True)),
                ('longitude', models.DecimalField(blank=True, db_column='longitude', decimal_places=8, max_digits=11, null=True)),
                ('city', models.CharField(blank=True, db_column='city', max_length=100, null=True)),
                ('post', models.CharField(blank=True, db_column='post', max_length=12, null=True)),
                ('water', models.CharField(blank=True, choices=[('r', 'river'), ('l', 'lake')], db_column='water', max_length=12, null=True)),
                ('water_name', models.CharField(blank=True, db_column='water_name', max_length=100, null=True)),
            ],
            options={
                'db_table': 'beaches',
                'ordering': ['location'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Codes',
            fields=[
                ('code', models.CharField(blank=True, db_column='code', max_length=5, primary_key=True, serialize=False)),
                ('material', models.CharField(blank=True, db_column='material', max_length=30, null=True)),
                ('description', models.CharField(blank=True, db_column='description', max_length=30, null=True)),
                ('source', models.CharField(blank=True, db_column='source', max_length=30, null=True)),
            ],
            options={
                'db_table': 'codes',
                'ordering': ['material'],
                'managed': True,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Finance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, db_column='date', null=True)),
                ('entry', models.CharField(choices=[('ex', 'expense'), ('re', 'revenue')], db_column='type', max_length=30)),
                ('origin', models.CharField(choices=[('t', 'Transportation'), ('m', 'Meals'), ('s', 'Software'), ('n', 'Network'), ('t', 'Telephone'), ('p', 'Personal equipment'), ('e', 'Equipment'), ('i', 'IT equipment'), ('o', 'Operations'), ('d', 'Donation'), ('s-g', 'Services group activity'), ('s-c', 'Services beach clean'), ('s-s', 'Services IT'), ('l', 'labor')], db_column='source', max_length=30)),
                ('amount', models.DecimalField(blank=True, db_column='amount', decimal_places=2, max_digits=10, null=True)),
                ('project', models.CharField(blank=True, db_column='project', max_length=30)),
            ],
            options={
                'db_table': 'finance',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='HDC_Beaches',
            fields=[
                ('location', models.CharField(blank=True, db_column='location', max_length=100, primary_key=True, serialize=False)),
                ('latitude', models.DecimalField(blank=True, db_column='latitude', decimal_places=8, max_digits=11, null=True)),
                ('longitude', models.DecimalField(blank=True, db_column='longitude', decimal_places=8, max_digits=11, null=True)),
                ('city', models.CharField(blank=True, db_column='city', max_length=100, null=True)),
                ('post', models.CharField(blank=True, db_column='post', max_length=12, null=True)),
                ('water', models.CharField(blank=True, choices=[('r', 'river'), ('l', 'lake')], db_column='water', max_length=12, null=True)),
                ('water_name', models.CharField(blank=True, db_column='water_name', max_length=100, null=True)),
            ],
            options={
                'db_table': 'hdrc_beaches',
                'ordering': ['location'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='HDC_Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, db_column='date', null=True)),
                ('length', models.IntegerField(db_column='length', default=0)),
                ('quantity', models.IntegerField(db_column='quantity', default=0)),
                ('code', models.ForeignKey(db_column='code', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Codes')),
                ('location', models.ForeignKey(db_column='location', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.HDC_Beaches')),
            ],
            options={
                'db_table': 'hdrc_data',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Precious',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, db_column='date', null=True)),
                ('length', models.IntegerField(db_column='length', default=0)),
                ('quantity', models.IntegerField(db_column='quantity', default=0)),
                ('code', models.ForeignKey(db_column='code', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Codes')),
                ('location', models.ForeignKey(db_column='location', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Beaches')),
            ],
            options={
                'db_table': 'precious',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Projects',
            fields=[
                ('project', models.CharField(blank=True, db_column='project', max_length=100, primary_key=True, serialize=False)),
                ('org', models.CharField(blank=True, db_column='org', max_length=100, null=True)),
            ],
            options={
                'db_table': 'projects',
                'ordering': ['project'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='References',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, db_column='title', max_length=240, null=True)),
                ('author', models.CharField(blank=True, db_column='author', max_length=120, null=True)),
                ('abstract', models.CharField(blank=True, db_column='abstract', max_length=300, null=True)),
                ('subject', models.CharField(choices=[('env', 'Environment - general'), ('env-h', 'Hydrology'), ('env-j', 'Environment - justice'), ('wat-q', 'Water quality'), ('bio', 'Biology - general'), ('chem', 'Chemistry'), ('m-bio', 'Microbiology'), ('b-l', 'Beach-litter'), ('econ', 'Economics'), ('cit', 'Citizen science'), ('gv', 'Government - reg'), ('mt', 'Math - general'), ('ma', 'Math - Analysis'), ('mp', 'Math - probability'), ('pp', 'Programing - python'), ('pd', 'Data science'), ('po', 'Programing - other'), ('gc', 'General culture')], db_column='subject', max_length=30)),
                ('project', models.ForeignKey(db_column='project', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Projects')),
            ],
            options={
                'db_table': 'library',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SLR_Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, db_column='date', null=True)),
                ('sample', models.IntegerField(blank=True, db_column='sample', null=True)),
                ('density2', models.DecimalField(blank=True, db_column='density2', decimal_places=3, max_digits=8)),
                ('quantity', models.IntegerField(db_column='quantity', default=0)),
            ],
            options={
                'db_table': 'slr_area',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SLR_Beaches',
            fields=[
                ('location', models.CharField(blank=True, db_column='Location', max_length=100, primary_key=True, serialize=False)),
                ('latitude', models.DecimalField(blank=True, db_column='latitude', decimal_places=8, max_digits=11, null=True)),
                ('longitude', models.DecimalField(blank=True, db_column='longitude', decimal_places=8, max_digits=11, null=True)),
                ('city', models.CharField(blank=True, db_column='city', max_length=100, null=True)),
                ('post', models.CharField(blank=True, db_column='post', max_length=12, null=True)),
                ('water', models.CharField(blank=True, choices=[('r', 'river'), ('l', 'lake')], db_column='water', max_length=12, null=True)),
                ('water_name', models.CharField(blank=True, db_column='water_name', max_length=100, null=True)),
                ('project', models.ForeignKey(db_column='project', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Projects')),
            ],
            options={
                'db_table': 'slr_beaches',
                'ordering': ['location'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SLR_Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, db_column='date', null=True)),
                ('length', models.IntegerField(db_column='length', default=0)),
                ('quantity', models.IntegerField(db_column='quantity', default=0)),
                ('density', models.DecimalField(blank=True, db_column='density', decimal_places=3, max_digits=8)),
                ('code', models.ForeignKey(db_column='code', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Codes')),
                ('location', models.ForeignKey(db_column='location', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.SLR_Beaches')),
                ('project', models.ForeignKey(db_column='project', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Projects')),
            ],
            options={
                'db_table': 'slr_data',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SLR_Density',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, db_column='date', null=True)),
                ('sample', models.IntegerField(blank=True, db_column='sample', null=True)),
                ('density', models.DecimalField(blank=True, db_column='density', decimal_places=3, max_digits=8)),
                ('quantity', models.IntegerField(blank=True, db_column='quantity', null=True)),
                ('location', models.ForeignKey(db_column='location', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.SLR_Beaches')),
                ('project', models.ForeignKey(db_column='project', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Projects')),
            ],
            options={
                'db_table': 'slr_dens_date',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='slr_area',
            name='location',
            field=models.ForeignKey(db_column='location', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.SLR_Beaches'),
        ),
        migrations.AddField(
            model_name='slr_area',
            name='project',
            field=models.ForeignKey(db_column='project', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Projects'),
        ),
        migrations.AddField(
            model_name='precious',
            name='project',
            field=models.ForeignKey(db_column='project', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Projects'),
        ),
        migrations.AddField(
            model_name='hdc_data',
            name='project',
            field=models.ForeignKey(db_column='project', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Projects'),
        ),
        migrations.AddField(
            model_name='hdc_beaches',
            name='project',
            field=models.ForeignKey(db_column='project', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Projects'),
        ),
        migrations.AddField(
            model_name='beaches',
            name='project',
            field=models.ForeignKey(db_column='project', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Projects'),
        ),
        migrations.AddField(
            model_name='all_data',
            name='code',
            field=models.ForeignKey(db_column='code', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Codes'),
        ),
        migrations.AddField(
            model_name='all_data',
            name='location',
            field=models.ForeignKey(db_column='location', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Beaches'),
        ),
        migrations.AddField(
            model_name='all_data',
            name='project',
            field=models.ForeignKey(db_column='project', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dirt.Projects'),
        ),
    ]
