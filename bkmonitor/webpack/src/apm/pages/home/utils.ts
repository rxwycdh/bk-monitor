/*
 * Tencent is pleased to support the open source community by making
 * 蓝鲸智云PaaS平台 (BlueKing PaaS) available.
 *
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 *
 * 蓝鲸智云PaaS平台 (BlueKing PaaS) is licensed under the MIT License.
 *
 * License for 蓝鲸智云PaaS平台 (BlueKing PaaS):
 *
 * ---------------------------------------------------
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
 * to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of
 * the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
 * THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 * CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */
import type { IOperateOption } from 'monitor-pc/pages/uptime-check/components/operate-options';

export const STATUS_MAP = {
  normal: {
    name: window.i18n.tc('正常'),
    style: {
      background: '#fff',
      color: '#313238',
    },
  },
  no_data: {
    name: window.i18n.tc('无数据'),
    style: {
      background: '#FFEEEE',
      color: '#EA3536',
    },
  },
  stop: {
    name: window.i18n.tc('已停止'),
    style: {
      background: '#F0F1F5',
      color: '#63656E',
    },
  },
  disabled: {
    name: window.i18n.tc('未开启'),
    style: {
      background: '#F0F1F5',
      color: '#63656E',
    },
  },
};

export const SEARCH_STATUS_LIST = [
  {
    id: 'normal',
    name: STATUS_MAP.normal.name,
  },
  {
    id: 'no_data',
    name: STATUS_MAP.no_data.name,
  },
  {
    id: 'stop',
    name: STATUS_MAP.stop.name,
  },
  {
    id: 'disabled',
    name: STATUS_MAP.disabled.name,
  },
];

export const SEARCH_KEYS = [
  {
    name: `Profiling ${window.i18n.t('数据状态')}`,
    id: 'profiling_data_status',
    children: SEARCH_STATUS_LIST,
  },
  {
    name: `Profiling ${window.i18n.t('是否启用')}`,
    id: 'is_enabled_profiling',
    children: [
      {
        id: 'true',
        name: window.i18n.t('是'),
      },
      {
        id: 'false',
        name: window.i18n.t('否'),
      },
    ],
  },
];

export const charColor = (str: string) => {
  const h = str.charCodeAt(0) % 360;
  const s = '50%';
  const l = '50%';
  const color = `hsl(${h}, ${s}, ${l})`;
  return color;
};

export const OPERATE_OPTIONS: IOperateOption[] = [
  {
    id: 'appDetails',
    name: window.i18n.t('应用详情'),
    authority: true,
  },
  {
    id: 'appConfig',
    name: window.i18n.t('应用配置'),
    authority: true,
  },
  {
    id: 'accessService',
    name: window.i18n.t('服务接入'),
    authority: true,
  },
  {
    id: 'noDataAlarm',
    name: window.i18n.t('新增无数据告警'),
    authority: true,
  },
  {
    id: 'delete',
    name: window.i18n.t('删除'),
    authority: true,
  },
];
