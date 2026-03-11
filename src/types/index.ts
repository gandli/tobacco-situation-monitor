export interface Clue {
  id: string;
  merchantName: string;
  platform: string;
  productDescription: string;
  price: number;
  originalPrice?: number;
  location: {
    province: string;
    city: string;
    district: string;
    address: string;
    lat: number;
    lng: number;
  };
  riskScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'investigating' | 'resolved' | 'dismissed';
  createTime: string;
  updateTime: string;
  evidence: Evidence[];
  relatedEntities: string[];
  tags: string[];
}

export interface Evidence {
  id: string;
  type: 'image' | 'video' | 'document' | 'screenshot' | 'link';
  title: string;
  description: string;
  url?: string;
  createTime: string;
}

export interface Case {
  id: string;
  clueId: string;
  caseNumber: string;
  title: string;
  status: 'draft' | 'submitted' | 'approved' | 'closed';
  createTime: string;
  updateTime: string;
  summary: string;
  details: string;
  evidence: Evidence[];
  involvedParties: Party[];
  timeline: TimelineEvent[];
}

export interface Party {
  id: string;
  type: 'merchant' | 'logistics' | 'person';
  name: string;
  role: string;
  contact?: string;
  address?: string;
  notes?: string;
}

export interface TimelineEvent {
  id: string;
  time: string;
  title: string;
  description: string;
  type: 'investigation' | 'evidence' | 'action' | 'decision';
}

export interface GraphNode {
  id: string;
  type: 'merchant' | 'logistics' | 'person';
  name: string;
  riskScore?: number;
  properties: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: 'supplies' | 'delivers' | 'owns' | 'works_for' | 'related';
  weight: number;
  properties: Record<string, any>;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface TrendData {
  date: string;
  totalClues: number;
  newClues: number;
  resolvedClues: number;
  highRiskClues: number;
}

export interface PlatformStats {
  platform: string;
  count: number;
  percentage: number;
  avgRiskScore: number;
}

export interface DashboardStats {
  totalClues: number;
  pendingClues: number;
  investigatingClues: number;
  resolvedClues: number;
  highRiskCount: number;
  todayNewClues: number;
  weeklyTrend: TrendData[];
  platformDistribution: PlatformStats[];
  recentClues: Clue[];
}