# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import functools

from alarm_backends.core.storage.redis import Cache
from apm_ebpf.apps import logger
from apm_ebpf.handlers import Installer, WorkloadContent
from constants.apm import BkCollectorComp


class BkCollectorInstaller(Installer):
    def __init__(self, cache, related_bk_biz_ids, *args, **kwargs):
        super(BkCollectorInstaller, self).__init__(*args, **kwargs)
        self.cache = cache
        self.related_bk_biz_ids = related_bk_biz_ids

    def check_installed(self):
        """
        检查集群是否安装了 bk-collector
        """
        namespace = BkCollectorComp.NAMESPACE

        found = False
        deployments = self.list_deployments(namespace)
        for deployment in deployments:
            content = WorkloadContent.deployment_to(deployment)
            if self.check_deployment(content, BkCollectorComp.DEPLOYMENT_NAME):
                found = True

        if found:
            # 将集群添加进缓存中 由 apm.tasks 中定时任务来继续执行
            self.cache.sadd(BkCollectorComp.CACHE_KEY_CLUSTER_IDS, self._generate_value)
            logger.info(f"[BkCollectorInstaller] add {self.cluster_id} to cache")

    @classmethod
    def generator(cls):
        # 避免重复创建连接
        cache = Cache("cache")
        while True:
            yield functools.partial(cls, cache=cache)

    @property
    def _generate_value(self):
        return f"{self.cluster_id}:{','.join(self.related_bk_biz_ids)}"
