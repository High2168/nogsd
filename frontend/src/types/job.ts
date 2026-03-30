/**
 * 职位相关类型定义
 *
 * 作者: 刘怀仁
 */

/**
 * 职位信息
 */
export interface Job {
  id: number
  title: string
  company_name?: string
  company_logo?: string
  company_size?: string
  company_industry?: string
  company?: Company
  salary_min: number
  salary_max: number
  salary_range?: string
  salary_note?: string
  location: string
  address?: string
  education_required: string
  experience_required: string
  description?: string
  requirements?: string
  category_name?: string
  tags?: JobTag[]
  skill_tags?: JobTag[]
  benefit_tags?: JobTag[]
  is_urgent?: boolean
  is_hot?: boolean
  view_count: number
  apply_count: number
  favorite_count: number
  match_score?: number
  match_reasons?: MatchReason[]
  is_favorite?: boolean
  is_applied?: boolean
  user_rating?: number
  published_at?: string
  created_at: string
}

/**
 * 公司信息
 */
export interface Company {
  id: number
  name: string
  logo?: string
  size?: string
  industry?: string
  description?: string
  address?: string
  website?: string
  financing_stage?: string
  job_count?: number
}

/**
 * 职位标签
 */
export interface JobTag {
  id: number
  name: string
  category: 'skill' | 'benefit' | 'industry' | 'other'
  color?: string
}

/**
 * 匹配理由
 */
export interface MatchReason {
  type: string
  desc: string
  score: number
}

/**
 * 职位列表响应
 */
export interface JobListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Job[]
}

/**
 * 职位搜索参数
 */
export interface JobSearchParams {
  keyword?: string
  location?: string
  salary_min?: number
  salary_max?: number
  education?: string
  experience?: string
  category?: number
  tags?: string
  ordering?: string
  page?: number
  page_size?: number
}
