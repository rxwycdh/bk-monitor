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
from collections import defaultdict

from opentelemetry.trace import StatusCode

from apm_web.constants import Apdex


class Calculation:
    @classmethod
    def instance_cal(cls, metric_result):
        if not metric_result:
            return 0

        return metric_result[0]["_result_"]

    @classmethod
    def range_cal(cls, metric_result):
        pass

    @classmethod
    def common_unify_result_cal_serie(cls, serie):
        return serie["datapoints"][0][0]

    @classmethod
    def calculate(cls, *data):
        return data[0]


class ErrorRateCalculation(Calculation):
    @classmethod
    def instance_cal(cls, metric_result):
        return cls.common_unify_result_cal(metric_result)

    @classmethod
    def common_unify_result_cal(cls, metric_result):
        sum_count = sum(i["_result_"] for i in metric_result)
        error_count = 0
        for serie in metric_result:
            if serie.get("status_code") == str(StatusCode.ERROR.value):
                error_count += serie["_result_"]

        return cls.calculate(error_count, sum_count)

    @classmethod
    def common_unify_series_cal(cls, series: []):
        sum_count = sum([serie["_result_"] for serie in series])
        error_count = 0
        for serie in series:
            if serie.get("status_code") == str(StatusCode.ERROR.value):
                error_count += serie["_result_"]
        return error_count, sum_count

    @classmethod
    def calculate(cls, *data):
        """
        输入为 (error_count, sum_count)
        """
        error_count, sum_count = data
        return error_count / (1 if sum_count == 0 else sum_count) * 100


class ApdexCalculation(Calculation):
    SATISFIED_RATE = 0.75
    TOLERATING_RATE = 0.5
    FRUSTRATING_RATE = 0.25

    @classmethod
    def instance_cal(cls, metric_result):
        return cls.common_unify_result_cal(metric_result)

    @classmethod
    def range_cal(cls, metric_result):
        datapoint_map = defaultdict(lambda: {"satisfied": 0, "tolerating": 0, "frustrated": 0, "error": 0})
        total_count = 0
        for serie in metric_result.get("series", []):
            for datapoint in serie["datapoints"]:
                if Apdex.DIMENSION_KEY not in serie["dimensions"]:
                    continue
                datapoint_value = datapoint[0]
                total_count += datapoint_value
                if serie["dimensions"].get("status_code") == str(StatusCode.ERROR.value):
                    datapoint_map[datapoint[1]]["error"] += datapoint_value
                if serie["dimensions"][Apdex.DIMENSION_KEY] == Apdex.SATISFIED:
                    datapoint_map[datapoint[1]]["satisfied"] += datapoint_value
                if serie["dimensions"][Apdex.DIMENSION_KEY] == Apdex.TOLERATING:
                    datapoint_map[datapoint[1]]["tolerating"] += datapoint_value
                if serie["dimensions"][Apdex.DIMENSION_KEY] == Apdex.FRUSTRATED:
                    datapoint_map[datapoint[1]]["frustrated"] += datapoint_value
        datapoints = []
        for datapoint, value in datapoint_map.items():
            if total_count:
                # 有数据
                apdex_rate = round(
                    (
                        (value["satisfied"] * 1)
                        + (value["frustrated"] * 0.5)
                        + ((value["tolerating"] + value["error"]) * 0)
                    )
                    / total_count,
                    2,
                )
                datapoints.append((apdex_rate, datapoint))
            else:
                # 无数据 则不显示此柱
                datapoints.append((None, datapoint))
        return {
            "metrics": [],
            "series": [{"datapoints": datapoints, "dimensions": {}, "target": "apdex", "type": "bar", "unit": ""}],
        }

    @classmethod
    def common_unify_result_cal(cls, metric_result):
        if not metric_result:
            return None

        error_count = sum(i["_result_"] for i in metric_result if i.get("status_code") == str(StatusCode.ERROR.value))
        total_count = 0
        satisfied_count = 0
        tolerating_count = 0
        frustrated_count = 0
        for serie in metric_result:
            if Apdex.DIMENSION_KEY not in serie:
                continue
            total_count += serie["_result_"]
            if serie[Apdex.DIMENSION_KEY] == Apdex.SATISFIED:
                satisfied_count += serie["_result_"]
            if serie[Apdex.DIMENSION_KEY] == Apdex.TOLERATING:
                tolerating_count += serie["_result_"]
            if serie[Apdex.DIMENSION_KEY] == Apdex.FRUSTRATED:
                frustrated_count += serie["_result_"]
        return cls.calculate(satisfied_count, tolerating_count, frustrated_count, error_count, total_count)

    @classmethod
    def calculate(cls, *data):
        # TODO 测试
        satisfied_count, tolerating_count, frustrated_count, error_count, total_count = data

        apdex_rate = (satisfied_count * 1 + tolerating_count * 0.5 + (tolerating_count + error_count) * 0) / total_count
        if apdex_rate > cls.SATISFIED_RATE:
            return Apdex.SATISFIED
        if apdex_rate > cls.TOLERATING_RATE:
            return Apdex.TOLERATING
        return Apdex.FRUSTRATED


class FlowMetricErrorRateCalculation(Calculation):
    """Flow 指标错误率计算"""

    def __init__(self, calculate_type):
        # choices: full / callee / caller
        self.calculate_type = calculate_type

    @classmethod
    def str_to_bool(cls, _str):
        return _str.lower() == "true"

    def range_cal(self, metric_result):
        """
        计算 Range 需要维度中包含 from_span_error / to_span_error
        此方法会忽略掉除 from_span_error / to_span_error 以外的维度
        所以如果查询中有其他维度不要使用此 Calculation
        """
        normal_ts = defaultdict(int)
        error_ts = defaultdict(int)
        all_ts = []

        for i, item in enumerate(metric_result.get("series", [])):
            if not item.get("datapoints"):
                continue

            dimensions = item.get("dimensions", {})
            if "from_span_error" not in dimensions or "to_span_error" not in dimensions:
                # 无效数据
                continue

            from_span_error, to_span_error = self.str_to_bool(dimensions["from_span_error"]), self.str_to_bool(
                dimensions["to_span_error"]
            )
            is_normal = not from_span_error and not to_span_error

            for value, timestamp in item["datapoints"]:
                if is_normal:
                    normal_ts[timestamp] = value

                if (
                    (self.calculate_type == "callee" and to_span_error)
                    or (self.calculate_type == "caller" and from_span_error)
                    or self.calculate_type == "full"
                ):
                    error_ts[timestamp] += value

                if i == 0:
                    all_ts.append(timestamp)

        return {
            "metrics": [],
            "series": [
                {
                    "datapoints": [
                        (round(error_ts.get(t, 0) / (normal_ts.get(t, 0) + error_ts.get(t, 0)), 2), t) for t in all_ts
                    ],
                    "dimensions": {},
                    "target": "flow",
                    "type": "bar",
                    "unit": "",
                }
            ],
        }

    def instance_cal(self, metric_result):

        total = sum([i.get("_result_", 0) for i in metric_result])
        if not total:
            return 0
        if self.calculate_type == "full":
            error_count = sum(
                [
                    i.get("_result_", 0)
                    for i in metric_result
                    if self.str_to_bool(i["from_span_error"]) or self.str_to_bool(i["to_span_error"])
                ]
            )
        elif self.calculate_type == "caller":
            error_count = sum([i.get("_result_", 0) for i in metric_result if self.str_to_bool(i["from_span_error"])])
        elif self.calculate_type == "callee":
            error_count = sum([i.get("_result_", 0) for i in metric_result if self.str_to_bool(i["to_span_error"])])
        else:
            raise ValueError(f"Not supported calculate type: {self.calculate_type}")

        return error_count / total
