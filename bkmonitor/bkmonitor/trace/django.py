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
import json
from typing import Any

from django.urls import Resolver404, resolve
from opentelemetry.trace import Span, Status, StatusCode

from core.errors import Error

# 参数最大字符限制
MAX_PARAMS_SIZE = 10000


def jsonify(data: Any) -> str:
    """尝试将数据转为 JSON 字符串"""
    try:
        return json.dumps(data)
    except (TypeError, ValueError):
        if isinstance(data, dict):
            return json.dumps({k: v for k, v in data.items() if not v or isinstance(v, (str, int, float, bool))})
        if isinstance(data, bytes):
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                return str(data)
        return str(data)


def request_hook(span: Span, request):
    """将请求中的 GET、BODY 参数记录在 span 中"""

    if not request:
        return

    if getattr(request, "FILES", None) and request.POST:
        # 请求中如果包含了文件 不取 Body 内容
        carrier = request.POST
    else:
        carrier = request.body

    body_str = jsonify(carrier) if carrier else ""
    param_str = jsonify(dict(request.GET)) if request.GET else ""

    span.set_attribute("request.body", body_str[:MAX_PARAMS_SIZE])
    span.set_attribute("request.params", param_str[:MAX_PARAMS_SIZE])


def response_hook(span, request, response):
    # Set user information as an attribute on the span
    if not request or not response:
        return

    user = getattr(request, "user", None)
    if user:
        username = getattr(user, "username", "")
    else:
        username = "unknown"
    span.set_attribute("user.username", username)

    if hasattr(response, "data"):
        result = response.data
    else:
        try:
            result = json.loads(response.content)
        except (TypeError, ValueError, AttributeError):
            return
    if not isinstance(result, dict):
        return

    res_result = result.get("result", True)
    span.set_attribute("response.code", result.get("code", 0))
    span.set_attribute("response.message", result.get("message", ""))
    span.set_attribute("response.result", str(res_result))
    if res_result:
        span.set_status(Status(StatusCode.OK))
    else:
        span.set_status(Status(StatusCode.ERROR))
        span.record_exception(exception=Error(result.get("message")))


def get_span_name(_, request):
    """获取 django instrument 生成的 span 的 span_name 返回 Resource的路径"""
    try:
        match = resolve(request.path)

        if hasattr(match, "func"):
            resource_clz = match.func.cls().resource_mapping.get(
                (request.method, match.func.actions.get(request.method.lower()))
            )
            if resource_clz:
                return f"{resource_clz.__module__}.{resource_clz.__qualname__}"

        if hasattr(match, "_func_name"):
            return match._func_name  # pylint: disable=protected-access # noqa

        return match.view_name
    except (Resolver404, AttributeError):
        return request.path
