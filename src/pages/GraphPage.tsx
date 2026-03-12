import React from 'react';
import { GraphVisualization } from '../components/graph/GraphVisualization';
import { generateGraphData } from '../data/mockData';
import type { GraphNode } from '../types';

export const GraphPage: React.FC = () => {
  const graphData = React.useMemo(() => generateGraphData(), []);

  const handleNodeClick = (node: GraphNode) => {
    console.log('Clicked node:', node);
  };

  return (
    <div className="space-y-6 lg:space-y-8 animate-fade-in">
      {/* 页面头部 */}
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight">
          关系图谱
        </h1>
        <p className="text-gray-500 mt-1">商家-物流-人员关联关系可视化</p>
      </div>

      {/* 图谱可视化 */}
      <GraphVisualization data={graphData} onNodeClick={handleNodeClick} />

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-5">
        <div className="bg-white rounded-xl border border-gray-200 p-5 lg:p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center">
              <span className="text-xl">店</span>
            </div>
            <div>
              <p className="text-sm text-gray-500">商家节点</p>
              <p className="text-2xl font-bold text-gray-900 tabular-nums">
                {graphData.nodes.filter(n => n.type === 'merchant').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5 lg:p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center">
              <span className="text-xl">运</span>
            </div>
            <div>
              <p className="text-sm text-gray-500">物流节点</p>
              <p className="text-2xl font-bold text-gray-900 tabular-nums">
                {graphData.nodes.filter(n => n.type === 'logistics').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5 lg:p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-purple-50 flex items-center justify-center">
              <span className="text-xl">人</span>
            </div>
            <div>
              <p className="text-sm text-gray-500">人员节点</p>
              <p className="text-2xl font-bold text-gray-900 tabular-nums">
                {graphData.nodes.filter(n => n.type === 'person').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 关系类型说明 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 lg:p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">关系类型说明</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex items-center gap-3 p-3 rounded-lg bg-gray-50">
            <div className="w-8 h-0.5 bg-blue-400 rounded-full" />
            <span className="text-sm text-gray-600">供应关系</span>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg bg-gray-50">
            <div className="w-8 h-0.5 bg-green-400 rounded-full" />
            <span className="text-sm text-gray-600">配送关系</span>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg bg-gray-50">
            <div className="w-8 h-0.5 bg-purple-400 rounded-full" />
            <span className="text-sm text-gray-600">拥有关系</span>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg bg-gray-50">
            <div className="w-8 h-0.5 bg-gray-400 rounded-full" />
            <span className="text-sm text-gray-600">关联关系</span>
          </div>
        </div>
      </div>
    </div>
  );
};