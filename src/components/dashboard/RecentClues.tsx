import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import type { Clue } from '../../types';
import { formatRelativeTime, getRiskColor, getRiskLabel, getStatusColor, getStatusLabel } from '../../utils/helpers';

interface RecentCluesProps {
  clues: Clue[];
}

export const RecentClues: React.FC<RecentCluesProps> = ({ clues }) => {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 lg:p-6 shadow-sm">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">最近线索</h3>
          <p className="text-sm text-gray-500 mt-0.5">最新录入的违法线索</p>
        </div>
        <Link 
          to="/clues" 
          className="flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 transition-colors group"
        >
          查看全部
          <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
        </Link>
      </div>
      
      <div className="space-y-2">
        {clues.slice(0, 5).map((clue, index) => (
          <Link
            key={clue.id}
            to={`/clues/${clue.id}`}
            className="
              group block p-4 rounded-xl
              bg-gray-50 hover:bg-gray-100
              border border-gray-100 hover:border-gray-200
              transition-all duration-200
            "
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1.5">
                  <h4 className="font-medium text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                    {clue.merchantName}
                  </h4>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getRiskColor(clue.riskLevel)}`}>
                    {getRiskLabel(clue.riskLevel)}
                  </span>
                </div>
                <p className="text-sm text-gray-500 truncate mb-2">{clue.productDescription}</p>
                <div className="flex items-center gap-3 text-xs text-gray-400">
                  <span className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-600">{clue.platform}</span>
                  <span className="w-1 h-1 rounded-full bg-gray-300" />
                  <span>{clue.location.city}</span>
                  <span className="w-1 h-1 rounded-full bg-gray-300" />
                  <span className="text-gray-600">¥{clue.price.toLocaleString()}</span>
                </div>
              </div>
              <div className="flex flex-col items-end gap-1.5">
                <span className={`inline-block px-2 py-1 rounded-lg text-xs font-medium ${getStatusColor(clue.status)}`}>
                  {getStatusLabel(clue.status)}
                </span>
                <p className="text-xs text-gray-400">{formatRelativeTime(clue.createTime)}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* 快速操作提示 */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <p className="text-xs text-gray-400 text-center">
          点击线索卡片查看详情并进行处置操作
        </p>
      </div>
    </div>
  );
};