/**
 * 推荐相关API
 *
 * 作者: 刘怀仁
 */

import { request } from './index'
import type { Job } from '@/types/job'

/**
 * 获取推荐职位
 */
export function getRecommendations(n: number = 10) {
  return request.get('/recommendations/', { params: { n } })
}

/**
 * 创建用户交互记录
 */
export function createInteraction(data: {
  job_id: number
  interaction_type: 'view' | 'favorite' | 'unfavorite' | 'apply' | 'rating'
  rating?: number
  duration?: number
  source?: string
}) {
  return request.post('/recommendations/interact/', data)
}

/**
 * 获取用户收藏列表
 */
export function getFavorites() {
  return request.get<Job[]>('/recommendations/favorites/')
}

/**
 * 获取用户交互历史
 */
export function getInteractionHistory() {
  return request.get('/recommendations/history/')
}

/**
 * 收藏职位
 */
export function favoriteJob(jobId: number) {
  return createInteraction({
    job_id: jobId,
    interaction_type: 'favorite',
  })
}

/**
 * 取消收藏
 */
export function unfavoriteJob(jobId: number) {
  return createInteraction({
    job_id: jobId,
    interaction_type: 'unfavorite',
  })
}

/**
 * 投递职位
 */
export function applyJob(jobId: number) {
  return createInteraction({
    job_id: jobId,
    interaction_type: 'apply',
  })
}

/**
 * 评分
 */
export function rateJob(jobId: number, rating: number) {
  return createInteraction({
    job_id: jobId,
    interaction_type: 'rating',
    rating,
  })
}
