/**
 * 用户相关类型定义
 */

/**
 * 用户画像
 */
export interface UserProfile {
  id: number
  username: string
  email: string
  name: string
  gender?: 'male' | 'female' | 'other'
  age?: number
  education?: string
  school?: string
  major?: string
  expected_position?: string
  expected_salary_min?: number
  expected_salary_max?: number
  salary_range?: string
  expected_cities?: string[]
  job_type?: string
  skills?: Skill[]
  skill_names?: string[]
  work_experience?: number
  experience_detail?: WorkExperience[]
  resume_url?: string
  introduction?: string
  created_at?: string
  updated_at?: string
}

/**
 * 技能
 */
export interface Skill {
  name: string
  level?: number  // 1-5
  years?: number
}

/**
 * 工作经历
 */
export interface WorkExperience {
  company: string
  position: string
  start_date: string
  end_date?: string
  description?: string
}
