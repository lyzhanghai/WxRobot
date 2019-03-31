# Generated by Django 2.1.7 on 2019-03-26 13:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plugs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ptitle', models.CharField(max_length=32, unique=True, verbose_name='插件名称')),
                ('pdescribe', models.TextField(verbose_name='插件描述')),
                ('plug_path', models.FileField(upload_to='static/upload/Plugs', verbose_name='插件文件')),
                ('wake_word', models.CharField(max_length=128)),
                ('isActive', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='SelectedFriends',
            fields=[
                ('fid', models.CharField(max_length=16, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='SelectedGroups',
            fields=[
                ('gid', models.CharField(max_length=16, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32, unique=True)),
                ('userpwd', models.CharField(max_length=32)),
                ('uemail', models.EmailField(max_length=254)),
                ('isActive', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserPlugs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isActive', models.BooleanField(default=True)),
                ('plug', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='databases.Plugs')),
                ('user_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='databases.UserInfo')),
            ],
        ),
        migrations.CreateModel(
            name='WechatId',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puid', models.CharField(max_length=32, unique=True)),
                ('isActive', models.BooleanField(default=True)),
                ('user_info', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='databases.UserInfo')),
            ],
        ),
        migrations.AddField(
            model_name='selectedgroups',
            name='wechat_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='databases.WechatId'),
        ),
        migrations.AddField(
            model_name='selectedfriends',
            name='wechat_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='databases.WechatId'),
        ),
    ]
