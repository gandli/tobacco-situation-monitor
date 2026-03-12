import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, MapPin, Calendar, Tag, AlertTriangle, Package, Truck, User } from 'lucide-react';
import { generateClues, generateCase } from '../data/mockData';
import { formatDate, getRiskColor, getRiskLabel, getStatusColor, getStatusLabel, getRiskBarColor, calculateDiscount, formatCurrency } from '../utils/helpers';
import { CaseDetail } from '../components/cases/CaseDetail';

export const ClueDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const clue = React.useMemo(() => {
    const clues = generateClues(50);
    return clues.find(c => c.id === id) || clues[0];
  }, [id]);

  const caseData = React.useMemo(() => generateCase(clue), [clue]);

  const discount = clue.originalPrice ? calculateDiscount(clue.price, clue.originalPrice) : 0;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 返回按钮 */}
      <button
        onClick={() => navigate('/clues')}
        className="flex items-center gap-2 text-gray-500 hover:text-gray-700 transition-colors group"
      >
        <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
        返回线索列表
      </button>

      {/* 线索头部信息 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 lg:p-6 shadow-sm">
        <div className="flex flex-col xl:flex-row xl:items-start justify-between gap-6">
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-3 mb-3">
              <h1 className="text-xl lg:text-2xl font-bold text-gray-900">{clue.merchantName}</h1>
              <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getRiskColor(clue.riskLevel)}`}>
                {getRiskLabel(clue.riskLevel)}
              </span>
              <span className={`px-3 py-1 rounded-lg text-sm font-medium ${getStatusColor(clue.status)}`}>
                {getStatusLabel(clue.status)}
              </span>
            </div>
            <p className="text-lg text-gray-600 mb-4">{clue.productDescription}</p>
            
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
              <div className="flex items-center gap-1.5">
                <Tag className="w-4 h-4 text-gray-400" />
                <span>{clue.platform}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-gray-400" />
                <span>{clue.location.province} {clue.location.city} {clue.location.district}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4 text-gray-400" />
                <span>{formatDate(clue.createTime)}</span>
              </div>
            </div>
          </div>

          <div className="xl:text-right flex-shrink-0">
            <div className="inline-block p-4 bg-gray-50 rounded-xl border border-gray-200">
              <div className="text-3xl font-bold text-gray-900 tabular-nums">
                {formatCurrency(clue.price)}
              </div>
              {clue.originalPrice && (
                <div className="text-lg text-gray-400 line-through tabular-nums mt-1">
                  {formatCurrency(clue.originalPrice)}
                </div>
              )}
              {discount > 0 && (
                <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 bg-red-50 text-red-600 rounded-lg text-sm font-medium">
                  <AlertTriangle className="w-4 h-4" />
                  低于市场价 {discount}%
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 风险评分 */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-gray-600">风险评分</span>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-gray-900 tabular-nums">{clue.riskScore}</span>
              <span className="text-sm text-gray-400">/ 100</span>
            </div>
          </div>
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${getRiskBarColor(clue.riskScore)}`}
              style={{ width: `${clue.riskScore}%` }}
            />
          </div>
          <p className="mt-2 text-xs text-gray-500">
            风险评分基于价格异常、平台信誉、历史记录等多维度计算
          </p>
        </div>

        {/* 标签 */}
        {clue.tags.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {clue.tags.map((tag) => (
              <span 
                key={tag} 
                className="px-3 py-1.5 bg-gray-100 text-gray-600 rounded-lg text-sm border border-gray-200"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* 快速概览卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
              <Package className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <p className="text-sm text-gray-500">商品平台</p>
              <p className="text-lg font-medium text-gray-900">{clue.platform}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center">
              <Truck className="w-5 h-5 text-green-500" />
            </div>
            <div>
              <p className="text-sm text-gray-500">发货地</p>
              <p className="text-lg font-medium text-gray-900">{clue.location.city}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center">
              <User className="w-5 h-5 text-purple-500" />
            </div>
            <div>
              <p className="text-sm text-gray-500">关联实体</p>
              <p className="text-lg font-medium text-gray-900 tabular-nums">{clue.relatedEntities.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* 地理位置详情 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 lg:p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-5 flex items-center gap-2">
          <MapPin className="w-5 h-5 text-gray-400" />
          地理位置
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <span className="text-sm text-gray-500 block mb-1">省份</span>
            <span className="text-gray-900 font-medium">{clue.location.province}</span>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <span className="text-sm text-gray-500 block mb-1">城市</span>
            <span className="text-gray-900 font-medium">{clue.location.city}</span>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <span className="text-sm text-gray-500 block mb-1">区县</span>
            <span className="text-gray-900 font-medium">{clue.location.district}</span>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 md:col-span-2">
            <span className="text-sm text-gray-500 block mb-1">详细地址</span>
            <span className="text-gray-900 font-medium">{clue.location.address}</span>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <span className="text-sm text-gray-500 block mb-1">坐标</span>
            <span className="text-gray-900 font-medium tabular-nums">
              {clue.location.lat.toFixed(4)}, {clue.location.lng.toFixed(4)}
            </span>
          </div>
        </div>
      </div>

      {/* 案件信息 */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          案件信息
        </h2>
        <CaseDetail caseData={caseData} />
      </div>
    </div>
  );
};