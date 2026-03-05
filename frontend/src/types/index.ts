// API Response Types

export interface KPIValue {
  value: number | null
  total?: number
  percentage: number
  description: string
}

export interface DashboardKPI {
  coverage_rate: KPIValue
  timeliness_score: KPIValue & { avg_hours: number | null }
  accuracy_rate: KPIValue
  noise_rate: KPIValue
  reviewable_rate: KPIValue
}

export interface RegionCount {
  region: string
  count: number
}

export interface DashboardSummary {
  today_new: number
  high_risk: number
  by_region: RegionCount[]
}

export interface Intel {
  id: number
  article_id: number
  is_case_related: boolean
  case_type: string | null
  region: string | null
  risk_score: number
  risk_level: 'low' | 'medium' | 'high'
  keywords_matched: string | null
  status: 'new' | 'reviewing' | 'confirmed' | 'dismissed'
}

export interface IntelListResponse {
  items: Intel[]
  total: number
}

export interface Source {
  id: number
  name: string
  list_url: string
  last_crawled_at: string | null
  created_at: string
  updated_at: string
}

export interface Alert {
  id: number
  intel_id: number
  alert_type: string | null
  message: string | null
  is_sent: boolean
  sent_at: string | null
  created_at: string
}

// Chart Types
export interface ChartDataItem {
  name: string
  value: number
}

export interface TimeSeriesData {
  date: string
  count: number
}