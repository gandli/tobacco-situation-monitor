import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays < 7) return `${diffDays}天前`;
  return formatDate(dateString);
}

export function getRiskColor(level: 'low' | 'medium' | 'high' | 'critical'): string {
  switch (level) {
    case 'critical': return 'text-red-600 bg-red-50 border-red-200';
    case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
    case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'low': return 'text-green-600 bg-green-50 border-green-200';
  }
}

export function getRiskLabel(level: 'low' | 'medium' | 'high' | 'critical'): string {
  switch (level) {
    case 'critical': return '极高风险';
    case 'high': return '高风险';
    case 'medium': return '中风险';
    case 'low': return '低风险';
  }
}

export function getStatusColor(status: 'pending' | 'investigating' | 'resolved' | 'dismissed'): string {
  switch (status) {
    case 'pending': return 'text-blue-600 bg-blue-50';
    case 'investigating': return 'text-orange-600 bg-orange-50';
    case 'resolved': return 'text-green-600 bg-green-50';
    case 'dismissed': return 'text-gray-600 bg-gray-50';
  }
}

export function getStatusLabel(status: 'pending' | 'investigating' | 'resolved' | 'dismissed'): string {
  switch (status) {
    case 'pending': return '待处理';
    case 'investigating': return '调查中';
    case 'resolved': return '已结案';
    case 'dismissed': return '已驳回';
  }
}