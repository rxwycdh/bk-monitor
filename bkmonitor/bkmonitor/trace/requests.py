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

from opentelemetry.trace import Span, Status, StatusCode


def requests_span_callback(span: Span, response):
    """将 requests 的请求和返回中的有用信息记录在 span 中"""
    if not response:
        return

    try:
        json_result = response.json()
    except Exception:  # pylint: disable=broad-except # noqa
        return

    if not isinstance(json_result, dict):
        return

    code = json_result.get("code", 0)
    errors = str(json_result.get("errors", ""))
    if errors:
        span.set_attribute("result_errors", errors)

    request_id = (
        response.headers.get("x-bkapi-request-id")
        or response.headers.get("x-request-id")
        or json_result.get("request_id", "")
    )
    if request_id:
        span.set_attribute("request_id", request_id)

    try:
        code_int = int(code)
        if code_int == 0 or code // 100 == 2:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR))
    except ValueError:
        if response.status_code // 100 == 2:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR))

    span.set_attribute("result_code", code)
    span.set_attribute("result_message", json_result.get("message", ""))

    req = response.request
    body = None
    if req.body:
        try:
            body = req.body.decode() if isinstance(req.body, bytes) else str(body)
            span.set_attribute("request.body", body)
        except Exception:  # noqa
            pass

    try:
        authorization_header = req.headers.get("x-bkapi-authorization")
        if authorization_header:
            username = json.loads(authorization_header).get("bk_username")
            if username:
                span.set_attribute("user.username", username)
    except (TypeError, json.JSONDecodeError):
        if body:
            try:
                username = json.loads(body).get("bk_username")
                if username:
                    span.set_attribute("user.username", username)
            except (TypeError, json.JSONDecodeError):
                pass


def requests_name_callback(method, _):
    return f"REQUESTS.HTTP {method.strip()}"
