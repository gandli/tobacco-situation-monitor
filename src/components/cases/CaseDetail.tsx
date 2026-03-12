import React from 'react';
import { 
  FileText, 
  Image, 
  Video, 
  Link, 
  File,
  User,
  MapPin,
  Clock,
  CheckCircle,
  AlertCircle,
  FileSearch,
  Download,
  ExternalLink,
  type LucideIcon
} from 'lucide-react';
import type { Evidence, Party, TimelineEvent, Case } from '../../types';
import { formatDate, getCaseStatusColor, getCaseStatusLabel, getTimelineEventColor } from '../../utils/helpers';

interface CaseDetailProps {
  caseData: Case;
}

// 证据类型图标映射
const evidenceIconMap: Record<Evidence['type'], LucideIcon> = {
  image: Image,
  video: Video,
  link: Link,
  screenshot: FileSearch,
  document: File,
};

const EvidenceCard: React.FC<{ evidence: Evidence }> = ({ evidence }) => {
  const Icon = evidenceIconMap[evidence.type] || File;

  return (
    <div className="group flex items-start gap-3 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors border border-gray-100">
      <div className="p-2.5 bg-white rounded-lg border border-gray-200">
        <Icon className="w-5 h-5 text-gray-500" />
      </div>
      <div className="flex-1 min-w-0">
        <h4 className="font-medium text-gray-900 truncate group-hover:text-blue-600 transition-colors">
          {evidence.title}
        </h4>
        <p className="text-sm text-gray-500 truncate mt-0.5">{evidence.description}</p>
        <p className="text-xs text-gray-400 mt-2">{formatDate(evidence.createTime)}</p>
      </div>
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        {evidence.url && (
          <a 
            href={evidence.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="p-1.5 rounded-lg bg-white border border-gray-200 text-gray-400 hover:text-gray-600 hover:border-gray-300 transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
        <button className="p-1.5 rounded-lg bg-white border border-gray-200 text-gray-400 hover:text-gray-600 hover:border-gray-300 transition-colors">
          <Download className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

const PartyCard: React.FC<{ party: Party }> = ({ party }) => {
  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'merchant': return '商家';
      case 'logistics': return '物流';
      case 'person': return '人员';
      default: return type;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'merchant': return 'bg-blue-50 text-blue-600 border-blue-200';
      case 'logistics': return 'bg-green-50 text-green-600 border-green-200';
      case 'person': return 'bg-purple-50 text-purple-600 border-purple-200';
      default: return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  return (
    <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-xl border border-gray-100 hover:border-gray-200 transition-colors">
      <div className={`
        w-12 h-12 rounded-xl flex items-center justify-center text-white font-medium text-lg
        ${party.type === 'merchant' ? 'bg-blue-100 text-blue-600' : 
          party.type === 'logistics' ? 'bg-green-100 text-green-600' : 'bg-purple-100 text-purple-600'}
      `}>
        {party.name.charAt(0)}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h4 className="font-medium text-gray-900">{party.name}</h4>
          <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getTypeColor(party.type)}`}>
            {getTypeLabel(party.type)}
          </span>
        </div>
        <p className="text-sm text-gray-500">{party.role}</p>
        {party.address && (
          <p className="text-sm text-gray-400 mt-1 flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {party.address}
          </p>
        )}
        {party.contact && (
          <p className="text-sm text-gray-400 mt-1">{party.contact}</p>
        )}
      </div>
    </div>
  );
};

const TimelineItem: React.FC<{ event: TimelineEvent; isLast: boolean }> = ({ event, isLast }) => {
  const getIcon = () => {
    switch (event.type) {
      case 'investigation': return <FileSearch className="w-4 h-4" />;
      case 'evidence': return <File className="w-4 h-4" />;
      case 'action': return <CheckCircle className="w-4 h-4" />;
      case 'decision': return <AlertCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center">
        <div className={`w-10 h-10 rounded-xl ${getTimelineEventColor(event.type)} text-white flex items-center justify-center shadow-sm`}>
          {getIcon()}
        </div>
        {!isLast && <div className="w-0.5 flex-1 bg-gray-200 mt-3 min-h-8" />}
      </div>
      <div className={`flex-1 pb-6 ${isLast ? 'pb-0' : ''}`}>
        <div className="flex flex-wrap items-center gap-2 mb-1.5">
          <h4 className="font-medium text-gray-900">{event.title}</h4>
          <span className="text-xs text-gray-400 px-2 py-0.5 bg-gray-100 rounded-full">
            {formatDate(event.time)}
          </span>
        </div>
        <p className="text-sm text-gray-600 leading-relaxed">{event.description}</p>
      </div>
    </div>
  );
};

export const CaseDetail: React.FC<CaseDetailProps> = ({ caseData }) => {
  return (
    <div className="space-y-6">
      {/* 案件头部 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 lg:p-6 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-3 mb-2">
              <h1 className="text-xl font-bold text-gray-900">{caseData.title}</h1>
              <span className={`px-3 py-1 rounded-lg text-sm font-medium ${getCaseStatusColor(caseData.status)}`}>
                {getCaseStatusLabel(caseData.status)}
              </span>
            </div>
            <p className="text-gray-500">案件编号: <span className="text-gray-700">{caseData.caseNumber}</span></p>
          </div>
          <div className="lg:text-right text-sm text-gray-500 space-y-1">
            <p>创建: {formatDate(caseData.createTime)}</p>
            <p>更新: {formatDate(caseData.updateTime)}</p>
          </div>
        </div>
      </div>

      {/* 案件摘要 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 lg:p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-gray-400" />
          案件摘要
        </h2>
        <p className="text-gray-600 leading-relaxed">{caseData.summary}</p>
      </div>

      {/* 详细信息 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 lg:p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-gray-400" />
          详细信息
        </h2>
        <div className="text-gray-600 leading-relaxed whitespace-pre-line">
          {caseData.details}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* 证据材料 */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 lg:p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-5 flex items-center gap-2">
            <File className="w-5 h-5 text-gray-400" />
            证据材料
            <span className="ml-auto text-sm font-normal text-gray-400 tabular-nums">
              ({caseData.evidence.length})
            </span>
          </h2>
          <div className="space-y-3">
            {caseData.evidence.map((ev) => (
              <EvidenceCard key={ev.id} evidence={ev} />
            ))}
          </div>
        </div>

        {/* 涉案方 */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 lg:p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-5 flex items-center gap-2">
            <User className="w-5 h-5 text-gray-400" />
            涉案方
            <span className="ml-auto text-sm font-normal text-gray-400 tabular-nums">
              ({caseData.involvedParties.length})
            </span>
          </h2>
          <div className="space-y-3">
            {caseData.involvedParties.map((party) => (
              <PartyCard key={party.id} party={party} />
            ))}
          </div>
        </div>
      </div>

      {/* 时间线 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 lg:p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
          <Clock className="w-5 h-5 text-gray-400" />
          处置时间线
        </h2>
        <div className="ml-1">
          {caseData.timeline.map((event, index) => (
            <TimelineItem 
              key={event.id} 
              event={event} 
              isLast={index === caseData.timeline.length - 1}
            />
          ))}
        </div>
      </div>
    </div>
  );
};