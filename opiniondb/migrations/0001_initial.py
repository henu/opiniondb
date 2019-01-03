# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BooleanOpinion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.BooleanField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LikeMinded',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('priority', models.IntegerField()),
                ('likeminded', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TagBelongsTo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TagCloud',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TagCloudGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='tagcloud',
            name='group',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='clouds', to='opiniondb.TagCloudGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tagbelongsto',
            name='cloud',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='tags', to='opiniondb.TagCloud'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tagbelongsto',
            name='tag',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='clouds', to='opiniondb.Tag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tagbelongsto',
            name='topic',
            field=models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='tag_belongs_to', to='opiniondb.Topic'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='tagbelongsto',
            unique_together=set([('tag', 'cloud')]),
        ),
        migrations.AddField(
            model_name='tag',
            name='group',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='tags', to='opiniondb.TagCloudGroup'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('name', 'group'), ('slug', 'group')]),
        ),
        migrations.AlterUniqueTogether(
            name='likeminded',
            unique_together=set([('user', 'likeminded')]),
        ),
        migrations.AddField(
            model_name='booleanopinion',
            name='topic',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='boolean_opinions', to='opiniondb.Topic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='booleanopinion',
            name='user',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='booleanopinion',
            unique_together=set([('user', 'topic')]),
        ),
    ]
