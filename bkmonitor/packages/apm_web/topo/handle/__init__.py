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
from typing import Type

from apm_web.metric_handler import MetricHandler
from apm_web.models import Application


class BaseQuery:
    def __init__(self, data_type, bk_biz_id, app_name, start_time, end_time, service_name=None, **extra_params):
        self.bk_biz_id = bk_biz_id
        self.app_name = app_name
        self.data_type = data_type
        self.start_time = start_time
        self.end_time = end_time
        self.delta = self.end_time - self.start_time
        self.params = extra_params
        self.filter_params = self.convert_to_condition(service_name)

        self.application = Application.objects.filter(bk_biz_id=bk_biz_id, app_name=app_name).get()
        self.metrics_table = self.application.metric_result_table_id

    def convert_to_condition(self, service_name) -> [dict, list]:
        return {"service_name": service_name}

    def get_metric(self, metric_clz: Type[MetricHandler], **kwargs):
        return metric_clz(**self.common_params, **kwargs)

    @property
    def common_params(self):
        return {
            "application": self.application,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }


class NodeDisplayType:
    """节点显示类型"""

    # 节点填充样式 正常 / 残影
    NORMAL = "normal"
    VOID = "void"

    # 节点边缘样式: 虚线 / 实线
    DASHED = "dashed"
    SOLID = "solid"

    UNDEFINED = "undefined"

    @classmethod
    def to_display(cls, ui_types):
        """拼接显示类型: {(dashed/solid)_{normal/void}}"""
        return "_".join(ui_types)
