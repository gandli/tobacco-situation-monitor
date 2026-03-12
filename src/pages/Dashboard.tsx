import React from 'react';
import { StatCards } from '../components/dashboard/StatCards';
import { TrendChart } from '../components/dashboard/TrendChart';
import { PlatformChart } from '../components/dashboard/PlatformChart';
import { RecentClues } from '../components/dashboard/RecentClues';
import { generateDashboardStats } from '../data/mockData';
import { RefreshCw, Calendar } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const stats = React.useMemo(() => generateDashboardStats(), []);
  const [isRefreshing, setIsRefreshing] = React.useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <div className="space-y-6 lg:space-y-8 animate-fade-in">
      {/* 页面头部 */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight">
            仪表板
          </h1>
          <p className="text-gray-500 mt-1">烟草执法态势感知概览</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg border border-gray-200">
            <Calendar className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600">
              {new Date().toLocaleDateString('zh-CN', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                weekday: 'long'
              })}
            </span>
          </div>
          <button 
            onClick={handleRefresh}
            className="p-2 rounded-lg bg-gray-100 border border-gray-200 text-gray-500 hover:text-gray-700 hover:bg-gray-200 transition-all"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* 统计卡片 */}
      <StatCards stats={stats} />

      {/* 图表行 */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 lg:gap-8">
        <TrendChart data={stats.weeklyTrend} />
        <PlatformChart data={stats.platformDistribution} />
      </div>

      {/* 最近线索 */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 lg:gap-8">
        <RecentClues clues={stats.recentClues} />
      </div>
    </div>
  );
};