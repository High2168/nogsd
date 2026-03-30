/**
 * 职位相关API
 *
 * 作者: 刘怀仁
 */

import { request } from './index'
import type { Job, JobListResponse, JobSearchParams } from '@/types/job'

/**
 * 获取职位列表
 */
export function getJobs(params?: JobSearchParams) {
  return request.get<JobListResponse>('/jobs/', { params })
}

/**
 * 获取职位详情
 */
export function getJobDetail(id: number) {
  return request.get<Job>(`/jobs/${id}/`)
}

/**
 * 搜索职位
 */
export function searchJobs(params: JobSearchParams) {
  return request.post<JobListResponse>('/jobs/search/', params)
}

/**
 * 获取热门职位
 */
export function getHotJobs() {
  return request.get('/jobs/hot/')
}

/**
 * 获取职位分类
 */
export function getJobCategories() {
  return request.get('/jobs/categories/')
}

/**
 * 获取职位标签
 */
export function getJobTags(params?: { category?: string }) {
  return request.get('/jobs/tags/', { params })
}
