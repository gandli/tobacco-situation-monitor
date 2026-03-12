import React from 'react';
import type { GraphData, GraphNode } from '../../types';

interface GraphVisualizationProps {
  data: GraphData;
  onNodeClick: (node: GraphNode) => void;
}

// 简单的图谱可视化组件（使用SVG）
export const GraphVisualization: React.FC<GraphVisualizationProps> = ({ data, onNodeClick }) => {
  const svgRef = React.useRef<SVGSVGElement>(null);
  const [dimensions, setDimensions] = React.useState({ width: 800, height: 500 });

  React.useEffect(() => {
    const updateDimensions = () => {
      if (svgRef.current?.parentElement) {
        const { clientWidth, clientHeight } = svgRef.current.parentElement;
        setDimensions({
          width: Math.max(800, clientWidth),
          height: Math.max(500, clientHeight)
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // 简单的力导向布局模拟
  const nodePositions = React.useMemo(() => {
    const positions: Record<string, { x: number; y: number }> = {};
    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;
    const radius = Math.min(dimensions.width, dimensions.height) * 0.35;

    // 按类型分组节点
    const merchants = data.nodes.filter(n => n.type === 'merchant');
    const logistics = data.nodes.filter(n => n.type === 'logistics');
    const persons = data.nodes.filter(n => n.type === 'person');

    // 放置商家节点（顶部弧）
    merchants.forEach((node, i) => {
      const angle = (Math.PI / (merchants.length + 1)) * (i + 1);
      positions[node.id] = {
        x: centerX + radius * Math.cos(angle - Math.PI / 2),
        y: centerY + radius * Math.sin(angle - Math.PI / 2) * 0.6
      };
    });

    // 放置物流节点（中部）
    logistics.forEach((node, i) => {
      positions[node.id] = {
        x: centerX - radius * 0.4 + (radius * 0.8 / logistics.length) * i,
        y: centerY + radius * 0.3
      };
    });

    // 放置人员节点（底部弧）
    persons.forEach((node, i) => {
      const angle = (Math.PI / (persons.length + 1)) * (i + 1);
      positions[node.id] = {
        x: centerX + radius * Math.cos(Math.PI + angle),
        y: centerY + radius * Math.sin(Math.PI + angle) * 0.4
      };
    });

    return positions;
  }, [data.nodes, dimensions]);

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'merchant': return '#3b82f6';
      case 'logistics': return '#22c55e';
      case 'person': return '#a855f7';
      default: return '#6b7280';
    }
  };

  const getEdgeColor = (type: string) => {
    switch (type) {
      case 'supplies': return '#3b82f6';
      case 'delivers': return '#22c55e';
      case 'owns': return '#a855f7';
      case 'related': return '#6b7280';
      default: return '#d1d5db';
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 lg:p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">关系图谱</h3>
          <p className="text-sm text-gray-500 mt-0.5">商家-物流-人员关联网络</p>
        </div>
      </div>
      
      <div className="h-96 lg:h-[500px] rounded-xl overflow-hidden border border-gray-100">
        <svg
          ref={svgRef}
          width="100%"
          height="100%"
          viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
          className="bg-gray-50"
        >
          {/* 定义箭头标记 */}
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="#9ca3af" />
            </marker>
          </defs>

          {/* 边 */}
          {data.edges.map((edge) => {
            const sourcePos = nodePositions[edge.source];
            const targetPos = nodePositions[edge.target];
            if (!sourcePos || !targetPos) return null;

            return (
              <line
                key={edge.id}
                x1={sourcePos.x}
                y1={sourcePos.y}
                x2={targetPos.x}
                y2={targetPos.y}
                stroke={getEdgeColor(edge.type)}
                strokeWidth={2}
                strokeOpacity={0.6}
                markerEnd="url(#arrowhead)"
              />
            );
          })}

          {/* 节点 */}
          {data.nodes.map((node) => {
            const pos = nodePositions[node.id];
            if (!pos) return null;

            return (
              <g key={node.id} onClick={() => onNodeClick(node)} className="cursor-pointer">
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={20}
                  fill={getNodeColor(node.type)}
                  stroke="white"
                  strokeWidth={3}
                  className="hover:opacity-80 transition-opacity"
                />
                <text
                  x={pos.x}
                  y={pos.y + 35}
                  textAnchor="middle"
                  fontSize={12}
                  fill="#374151"
                  fontWeight={500}
                >
                  {node.name.slice(0, 4)}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      
      {/* 图例 */}
      <div className="mt-4 flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
        <span className="text-gray-500 font-medium">节点类型:</span>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-blue-500" />
          <span className="text-gray-600">商家</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-green-500" />
          <span className="text-gray-600">物流</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-purple-500" />
          <span className="text-gray-600">人员</span>
        </div>
      </div>
    </div>
  );
};