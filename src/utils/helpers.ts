// 日期格式化
export const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
};

export const formatRelativeTime = (dateStr: string): string => {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays < 7) return `${diffDays}天前`;
  return formatDate(dateStr);
};

// 货币格式化
export const formatCurrency = (amount: number): string => {
  return `¥${amount.toLocaleString('zh-CN')}`;
};

// 折扣计算
export const calculateDiscount = (price: number, originalPrice: number): number => {
  if (originalPrice <= 0) return 0;
  return Math.round(((originalPrice - price) / originalPrice) * 100);
};

// 风险等级
export const getRiskLabel = (level: string): string => {
  switch (level) {
    case 'critical': return '极高风险';
    case 'high': return '高风险';
    case 'medium': return '中风险';
    case 'low': return '低风险';
    default: return '未知';
  }
};

export const getRiskColor = (level: string): string => {
  switch (level) {
    case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/30';
    case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
    case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    case 'low': return 'bg-green-500/20 text-green-400 border-green-500/30';
    default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  }
};

export const getRiskBarColor = (score: number): string => {
  if (score >= 80) return 'bg-red-500';
  if (score >= 60) return 'bg-orange-500';
  if (score >= 40) return 'bg-yellow-500';
  return 'bg-green-500';
};

// 状态
export const getStatusLabel = (status: string): string => {
  switch (status) {
    case 'pending': return '待处理';
    case 'investigating': return '调查中';
    case 'resolved': return '已结案';
    case 'dismissed': return '已驳回';
    default: return '未知';
  }
};

export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'pending': return 'bg-yellow-500/20 text-yellow-400';
    case 'investigating': return 'bg-blue-500/20 text-blue-400';
    case 'resolved': return 'bg-green-500/20 text-green-400';
    case 'dismissed': return 'bg-gray-500/20 text-gray-400';
    default: return 'bg-gray-500/20 text-gray-400';
  }
};

// 案件状态
export const getCaseStatusLabel = (status: string): string => {
  switch (status) {
    case 'draft': return '草稿';
    case 'submitted': return '已提交';
    case 'approved': return '已批准';
    case 'closed': return '已关闭';
    default: return '未知';
  }
};

export const getCaseStatusColor = (status: string): string => {
  switch (status) {
    case 'draft': return 'bg-gray-500/20 text-gray-400';
    case 'submitted': return 'bg-yellow-500/20 text-yellow-400';
    case 'approved': return 'bg-blue-500/20 text-blue-400';
    case 'closed': return 'bg-green-500/20 text-green-400';
    default: return 'bg-gray-500/20 text-gray-400';
  }
};

// 时间线事件颜色
export const getTimelineEventColor = (type: string): string => {
  switch (type) {
    case 'investigation': return 'bg-blue-500';
    case 'evidence': return 'bg-purple-500';
    case 'action': return 'bg-green-500';
    case 'decision': return 'bg-orange-500';
    default: return 'bg-gray-500';
  }
};