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
import operator

from django.db.models import Q
from django.utils.datetime_safe import datetime

from apm_ebpf.apps import logger
from apm_ebpf.models import ClusterRelation
from core.drf_resource import api


class RelationHandler:
    @classmethod
    def find_clusters(cls):
        """
        BCS集群发现
        """
        clusters = api.bcs_cluster_manager.get_project_clusters(exclude_shared_cluster=True)

        cluster_mapping = cls.group_by(clusters, operator.itemgetter("cluster_id"))

        add_keys = []
        update_ids = []
        delete_ids = []

        for cluster_id, items in cluster_mapping.items():
            exists_mappings = {
                (str(i.bk_biz_id), i.project_id, i.cluster_id): i.id
                for i in ClusterRelation.objects.filter(cluster_id=cluster_id)
            }
            for item in items:
                key = (item["bk_biz_id"], item["project_id"], item["cluster_id"])
                if key in exists_mappings:
                    update_ids.append(exists_mappings[key])
                    del exists_mappings[key]
                else:
                    add_keys.append(key)

            delete_ids += list(exists_mappings.values())

        ClusterRelation.objects.filter(id__in=update_ids).update(last_check_time=datetime.now())
        ClusterRelation.objects.filter(Q(id__in=delete_ids) | ~Q(id__in=update_ids)).delete()
        add_instances = [
            ClusterRelation(bk_biz_id=i[0], project_id=i[1], cluster_id=i[2], last_check_time=datetime.now())
            for i in add_keys
        ]
        ClusterRelation.objects.bulk_create(add_instances)
        logger.info(f"[find_cluster] add: {len(add_instances)}, update: {len(update_ids)}, delete: {len(delete_ids)}")

    @classmethod
    def group_by(cls, iterators, get_key):
        res = {}
        for item in iterators:
            key = get_key(item)
            if not key:
                continue

            if key in res:
                res[key].append(item)
            else:
                res[key] = [item]

        return res

    @classmethod
    def list_biz_ids(cls, cluster_id):
        """
        根据集群ID获取关联的业务ID列表
        """
        return list(
            ClusterRelation.objects.filter(cluster_id=cluster_id).values_list("bk_biz_id", flat=True).distinct()
        )
