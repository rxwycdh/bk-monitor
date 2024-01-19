/*
 * Tencent is pleased to support the open source community by making
 * 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 *
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 *
 * 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) is licensed under the MIT License.
 *
 * License for 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition):
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

import { computed, defineComponent, inject, PropType, Ref, ref, watch } from 'vue';
import { Exception, Loading } from 'bkui-vue';
import { debounce } from 'throttle-debounce';

import { query } from '../../../../monitor-api/modules/apm_profile';
import { BaseDataType, ProfilingTableItem, ViewModeType } from '../../../../monitor-ui/chart-plugins/typings';
import { handleTransformToTimestamp } from '../../../components/time-range/utils';
import { ToolsFormData } from '../../../pages/profiling/typings';
import { DirectionType, IQueryParams } from '../../../typings';

import ChartTitle from './chart-title/chart-title';
import FrameGraph from './flame-graph/flame-graph';
import TableGraph from './table-graph/table-graph';
import TopoGraph from './topo-graph/topo-graph';

import './profiling-graph.scss';

export default defineComponent({
  name: 'ProfilingGraph',
  props: {
    queryParams: {
      type: Object as PropType<IQueryParams>,
      default: () => ({})
    }
  },
  setup(props) {
    const toolsFormData = inject<Ref<ToolsFormData>>('toolsFormData');

    const frameGraphRef = ref(FrameGraph);
    const empty = ref(true);
    // 当前视图模式
    const activeMode = ref<ViewModeType>(ViewModeType.Combine);
    const textDirection = ref<DirectionType>('ltr');
    const isLoading = ref(false);
    const tableData = ref<ProfilingTableItem[]>([]);
    const flameData = ref<BaseDataType>({
      name: '',
      children: undefined,
      id: ''
    });
    const unit = ref('');
    const highlightId = ref(-1);
    const filterKeyword = ref('');
    const topoSrc = ref('');

    const flameFilterKeywords = computed(() => (filterKeyword.value?.trim?.().length ? [filterKeyword.value] : []));

    watch(
      [() => props.queryParams],
      debounce(16, async () => handleQuery()),
      {
        immediate: true,
        deep: true
      }
    );
    watch(
      () => toolsFormData.value.timeRange,
      () => {
        handleQuery();
      },
      {
        deep: true
      }
    );

    const getParams = (args: Record<string, any> = {}) => {
      const { queryParams } = props;
      const [start, end] = handleTransformToTimestamp(toolsFormData.value.timeRange);
      return {
        ...args,
        ...queryParams,
        start: start * Math.pow(10, 6),
        end: end * Math.pow(10, 6),
        // TODO
        app_name: 'profiling_bar',
        service_name: 'fuxi_gin'
      };
    };
    const handleQuery = async () => {
      try {
        isLoading.value = true;
        highlightId.value = -1;
        const params = getParams({ diagram_types: ['table', 'flamegraph'] });
        const data = await query(params).catch(() => false);
        if (data.diagrams) {
          unit.value = data.diagrams.unit || '';
          tableData.value = data.diagrams.table_data || [];
          flameData.value = data.diagrams.flame_data;
          empty.value = false;
        } else {
          empty.value = true;
        }
        isLoading.value = false;
      } catch (e) {
        console.error(e);
        isLoading.value = false;
        empty.value = true;
      }
    };
    /** 切换视图模式 */
    const handleModeChange = async (val: ViewModeType) => {
      if (val === activeMode.value) return;

      highlightId.value = -1;
      activeMode.value = val;

      if (val === ViewModeType.Topo && !topoSrc.value) {
        isLoading.value = true;

        const params = getParams({ diagram_types: ['callgraph'] });
        const data = await query(params).catch(() => false);
        if (data.diagrams) {
          topoSrc.value = data.diagrams.call_graph_data || '';
        }
        isLoading.value = false;
      }
    };
    const handleTextDirectionChange = (val: DirectionType) => {
      textDirection.value = val;
    };
    /** 表格排序 */
    const handleSortChange = async (sortKey: string) => {
      const params = getParams({
        diagram_types: ['table'],
        sort: sortKey
      });
      const data = await query(params).catch(() => false);
      if (data.diagrams) {
        highlightId.value = -1;
        tableData.value = data.diagrams.table_data || [];
      }
    };
    /** 下载 */
    const handleDownload = (type: string) => {
      switch (type) {
        case 'png':
          frameGraphRef.value?.handleStoreImg();
          break;
        case 'pprof':
          break;
        default:
          break;
      }
    };

    return {
      frameGraphRef,
      empty,
      tableData,
      flameData,
      unit,
      isLoading,
      activeMode,
      textDirection,
      handleModeChange,
      handleTextDirectionChange,
      highlightId,
      filterKeyword,
      flameFilterKeywords,
      handleSortChange,
      handleDownload,
      topoSrc
    };
  },
  render() {
    return (
      <Loading
        loading={this.isLoading}
        class='profiling-graph'
      >
        <ChartTitle
          activeMode={this.activeMode}
          textDirection={this.textDirection}
          onModeChange={this.handleModeChange}
          onTextDirectionChange={this.handleTextDirectionChange}
          onKeywordChange={val => (this.filterKeyword = val)}
          onDownload={this.handleDownload}
        />
        {this.empty ? (
          <Exception
            type='empty'
            description={this.$t('暂无数据')}
          />
        ) : (
          <div class='profiling-graph-content'>
            {[ViewModeType.Combine, ViewModeType.Table].includes(this.activeMode) && (
              <TableGraph
                data={this.tableData}
                unit={this.unit}
                textDirection={this.textDirection}
                highlightId={this.highlightId}
                filterKeyword={this.filterKeyword}
                onUpdateHighlightId={id => (this.highlightId = id)}
                onSortChange={this.handleSortChange}
              />
            )}
            {[ViewModeType.Combine, ViewModeType.Flame].includes(this.activeMode) && (
              <FrameGraph
                ref='frameGraphRef'
                textDirection={this.textDirection}
                showGraphTools={false}
                data={this.flameData}
                highlightId={this.highlightId}
                filterKeywords={this.flameFilterKeywords}
                onUpdateHighlightId={id => (this.highlightId = id)}
              />
            )}
            {ViewModeType.Topo === this.activeMode && <TopoGraph topoSrc={this.topoSrc} />}
          </div>
        )}
      </Loading>
    );
  }
});
