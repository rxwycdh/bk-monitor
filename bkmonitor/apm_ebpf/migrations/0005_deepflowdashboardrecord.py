# Generated by Django 3.2.15 on 2024-02-27 06:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("apm_ebpf", "0004_merge_20231211_1735"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeepflowDashboardRecord",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bk_biz_id", models.IntegerField(verbose_name="监控的容器项目业务ID 可能为负数")),
                ("name", models.CharField(max_length=526, verbose_name="仪表盘名称")),
            ],
            options={
                "verbose_name": "deepflow仪表盘安装记录",
            },
        ),
    ]
