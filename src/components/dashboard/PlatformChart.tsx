import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import type { PlatformStats } from '../../types';

interface PlatformChartProps {
  data: PlatformStats[];
}

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

export const PlatformChart: React.FC<PlatformChartProps> = ({ data }) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">平台分布</h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={true} vertical={false} />
            <XAxis type="number" stroke="#9ca3af" fontSize={12} />
            <YAxis 
              type="category" 
              dataKey="platform" 
              stroke="#9ca3af" 
              fontSize={12}
              width={60}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              }}
              formatter={(value, name) => {
                const numValue = typeof value === 'number' ? value : 0;
                const strName = String(name);
                if (strName === 'count') return [numValue, '线索数量'];
                if (strName === 'avgRiskScore') return [numValue, '平均风险分'];
                return [numValue, strName];
              }}
            />
            <Bar dataKey="count" name="count" radius={[0, 4, 4, 0]}>
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      {/* Platform list */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
        {data.slice(0, 8).map((item, index) => (
          <div key={item.platform} className="flex items-center gap-2">
            <div 
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: COLORS[index % COLORS.length] }}
            />
            <span className="text-sm text-gray-600">{item.platform}</span>
            <span className="text-sm font-medium text-gray-900 ml-auto">{item.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
};