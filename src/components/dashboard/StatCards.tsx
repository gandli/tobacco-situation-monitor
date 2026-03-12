import React from 'react';
import { 
  AlertTriangle, 
  FileSearch, 
  Clock, 
  CheckCircle,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import type { DashboardStats } from '../../types';

interface StatCardsProps {
  stats: DashboardStats;
}

export const StatCards: React.FC<StatCardsProps> = ({ stats }) => {
  const cards = [
    {
      title: '总线索数',
      value: stats.totalClues,
      icon: FileSearch,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: '待处理',
      value: stats.pendingClues,
      icon: Clock,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
    {
      title: '调查中',
      value: stats.investigatingClues,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: '已结案',
      value: stats.resolvedClues,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: '高风险',
      value: stats.highRiskCount,
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      title: '今日新增',
      value: stats.todayNewClues,
      icon: TrendingDown,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {cards.map((card) => (
        <div
          key={card.title}
          className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${card.bgColor}`}>
              <card.icon className={`w-5 h-5 ${card.color}`} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-500 truncate">{card.title}</p>
              <p className="text-2xl font-bold text-gray-900">{card.value}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};