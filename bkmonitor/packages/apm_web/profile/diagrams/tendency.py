"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


class TendencyDiagrammer:
    field_key = "(round((cast(dtEventTimeStamp as DOUBLE) / cast(60000 as DOUBLE))) * cast(60 as DOUBLE))"
    value_key = "sum(value)"

    def draw(self, c: dict, **options) -> dict:
        """statistics profile data by time"""

        # follow the structure of bk-ui plugin
        return {
            "series": [
                {
                    "alias": "_result_",
                    "datapoints": [
                        [int(i[self.field_key]), i[self.value_key]] for i in c.get("list", []) if self.field_key in i
                    ],
                    "type": "line",
                    "unit": "",
                }
            ]
        }

    def diff(self, base_doris_converter: dict, diff_doris_converter: dict, **options) -> dict:
        """diff two profile data by time"""

        # follow the structure of bk-ui plugin
        return {
            "series": [
                {
                    "alias": "_result_",
                    "datapoints": [
                        [int(i[self.field_key]), i[self.value_key]]
                        for i in base_doris_converter.get("list", [])
                        if self.field_key in i
                    ],
                    "type": "line",
                    "unit": "",
                    "dimensions": {"device_name": '查询项'},
                },
                {
                    "alias": "_result_",
                    "datapoints": [
                        [int(i[self.field_key]), i[self.value_key]]
                        for i in diff_doris_converter.get("list", [])
                        if self.field_key in i
                    ],
                    "type": "line",
                    "unit": "",
                    "dimensions": {"device_name": '对比项'},
                },
            ]
        }
