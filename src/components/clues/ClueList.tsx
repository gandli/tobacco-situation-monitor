import React from 'react';
import { Search, Filter, MapPin, Calendar, ChevronRight } from 'lucide-react';
import type { Clue } from '../../types';
import { formatDate, getRiskColor, getRiskLabel, getStatusColor, getStatusLabel, getRiskBarColor } from '../../utils/helpers';

interface ClueCardProps {
  clue: Clue;
  onClick: () => void;
}

export const ClueCard: React.FC<ClueCardProps> = ({ clue, onClick }) => {
  return (
    <div
      onClick={onClick}
      className="
        group relative
        bg-white
        rounded-xl border border-gray-200
        p-5 lg:p-6
        cursor-pointer
        transition-all duration-200
        hover:border-gray-300
        hover:shadow-lg
      "
    >
      {/* 顶部信息 */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <h3 className="font-semibold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
              {clue.merchantName}
            </h3>
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium border flex-shrink-0 ${getRiskColor(clue.riskLevel)}`}>
              {getRiskLabel(clue.riskLevel)}
            </span>
          </div>
          <p className="text-sm text-gray-500 line-clamp-2">{clue.productDescription}</p>
        </div>
        <div className="text-right ml-4 flex-shrink-0">
          <div className="text-xl font-bold text-gray-900 tabular-nums">¥{clue.price.toLocaleString()}</div>
          {clue.originalPrice && (
            <div className="text-xs text-gray-400 line-through tabular-nums">¥{clue.originalPrice.toLocaleString()}</div>
          )}
        </div>
      </div>

      {/* 元信息 */}
      <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
        <div className="flex items-center gap-1.5">
          <MapPin className="w-4 h-4 text-gray-400" />
          <span>{clue.location.city}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Calendar className="w-4 h-4 text-gray-400" />
          <span>{formatDate(clue.createTime)}</span>
        </div>
      </div>

      {/* 标签和状态 */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="px-2.5 py-1 bg-blue-50 text-blue-600 rounded-lg text-xs font-medium">
            {clue.platform}
          </span>
          <span className={`px-2.5 py-1 rounded-lg text-xs font-medium ${getStatusColor(clue.status)}`}>
            {getStatusLabel(clue.status)}
          </span>
        </div>
        <div className="flex items-center gap-1">
          {clue.tags.slice(0, 2).map((tag) => (
            <span key={tag} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* 风险评分条 */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
          <span>风险评分</span>
          <span className="font-medium text-gray-700 tabular-nums">{clue.riskScore}/100</span>
        </div>
        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-300 ${getRiskBarColor(clue.riskScore)}`}
            style={{ width: `${clue.riskScore}%` }}
          />
        </div>
      </div>

      {/* 悬停指示 */}
      <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
        <ChevronRight className="w-5 h-5 text-blue-500" />
      </div>
    </div>
  );
};

interface ClueListProps {
  clues: Clue[];
  onClueClick: (clue: Clue) => void;
}

export const ClueList: React.FC<ClueListProps> = ({ clues, onClueClick }) => {
  const [searchTerm, setSearchTerm] = React.useState('');
  const [selectedPlatform, setSelectedPlatform] = React.useState<string>('all');
  const [selectedRisk, setSelectedRisk] = React.useState<string>('all');
  const [selectedStatus, setSelectedStatus] = React.useState<string>('all');

  const platforms = ['all', ...new Set(clues.map(c => c.platform))];

  const filteredClues = clues.filter(clue => {
    const matchesSearch = 
      clue.merchantName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      clue.productDescription.toLowerCase().includes(searchTerm.toLowerCase()) ||
      clue.location.city.includes(searchTerm);
    const matchesPlatform = selectedPlatform === 'all' || clue.platform === selectedPlatform;
    const matchesRisk = selectedRisk === 'all' || clue.riskLevel === selectedRisk;
    const matchesStatus = selectedStatus === 'all' || clue.status === selectedStatus;
    
    return matchesSearch && matchesPlatform && matchesRisk && matchesStatus;
  });

  return (
    <div>
      {/* 筛选栏 */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 lg:p-5 mb-6 shadow-sm">
        <div className="flex flex-col xl:flex-row gap-4">
          {/* 搜索框 */}
          <div className="flex-1 relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="搜索商家、商品、城市..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="
                w-full pl-11 pr-4 py-2.5
                bg-gray-50 border border-gray-200
                rounded-xl text-gray-900 placeholder:text-gray-400
                focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500
                transition-all
              "
            />
          </div>

          {/* 筛选器 */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 text-gray-400">
              <Filter className="w-4 h-4" />
            </div>

            {/* 平台筛选 */}
            <select
              value={selectedPlatform}
              onChange={(e) => setSelectedPlatform(e.target.value)}
              className="
                px-3.5 py-2.5
                bg-gray-50 border border-gray-200
                rounded-xl text-gray-700
                focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500
                transition-all cursor-pointer
              "
            >
              <option value="all">所有平台</option>
              {platforms.filter(p => p !== 'all').map(platform => (
                <option key={platform} value={platform}>{platform}</option>
              ))}
            </select>

            {/* 风险筛选 */}
            <select
              value={selectedRisk}
              onChange={(e) => setSelectedRisk(e.target.value)}
              className="
                px-3.5 py-2.5
                bg-gray-50 border border-gray-200
                rounded-xl text-gray-700
                focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500
                transition-all cursor-pointer
              "
            >
              <option value="all">所有风险</option>
              <option value="critical">极高风险</option>
              <option value="high">高风险</option>
              <option value="medium">中风险</option>
              <option value="low">低风险</option>
            </select>

            {/* 状态筛选 */}
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="
                px-3.5 py-2.5
                bg-gray-50 border border-gray-200
                rounded-xl text-gray-700
                focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500
                transition-all cursor-pointer
              "
            >
              <option value="all">所有状态</option>
              <option value="pending">待处理</option>
              <option value="investigating">调查中</option>
              <option value="resolved">已结案</option>
              <option value="dismissed">已驳回</option>
            </select>
          </div>
        </div>

        {/* 结果统计 */}
        <div className="mt-4 flex items-center justify-between text-sm">
          <p className="text-gray-500">
            共找到 <span className="font-medium text-gray-900 tabular-nums">{filteredClues.length}</span> 条线索
          </p>
          {(selectedPlatform !== 'all' || selectedRisk !== 'all' || selectedStatus !== 'all' || searchTerm) && (
            <button 
              onClick={() => {
                setSearchTerm('');
                setSelectedPlatform('all');
                setSelectedRisk('all');
                setSelectedStatus('all');
              }}
              className="text-blue-600 hover:text-blue-700 transition-colors"
            >
              清除筛选
            </button>
          )}
        </div>
      </div>

      {/* 线索卡片网格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 lg:gap-5">
        {filteredClues.map((clue, index) => (
          <div 
            key={clue.id} 
            className="animate-fade-in"
            style={{ animationDelay: `${index * 30}ms` }}
          >
            <ClueCard clue={clue} onClick={() => onClueClick(clue)} />
          </div>
        ))}
      </div>

      {/* 空状态 */}
      {filteredClues.length === 0 && (
        <div className="text-center py-16 bg-gray-50 rounded-xl border border-gray-200">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
            <Search className="w-8 h-8 text-gray-400" />
          </div>
          <p className="text-gray-500 mb-2">没有找到匹配的线索</p>
          <p className="text-sm text-gray-400">尝试调整筛选条件或搜索关键词</p>
        </div>
      )}
    </div>
  );
};