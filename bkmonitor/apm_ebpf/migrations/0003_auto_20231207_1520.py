# Generated by Django 3.2.15 on 2023-12-07 07:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('apm_ebpf', '0002_clusterrelation'),
    ]

    operations = [
        migrations.AddField(
            model_name='clusterrelation',
            name='related_bk_biz_id',
            field=models.IntegerField(default=None, verbose_name='集群关联的BKCC业务id'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='clusterrelation',
            name='bk_biz_id',
            field=models.IntegerField(verbose_name='监控的容器项目业务ID 可能为负数'),
        ),
        migrations.AlterField(
            model_name='deepflowworkload',
            name='last_check_time',
            field=models.DateTimeField(verbose_name='最后检查日期'),
        ),
    ]
