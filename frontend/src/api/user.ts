/**
 * 用户相关API
 */

import { request } from './index'
import type { UserProfile } from '@/types/user'

// ==================== 认证相关 ====================

/**
 * 用户登录
 */
export function login(data: { username: string; password: string }) {
  return request.post('/auth/login/', data)
}

/**
 * 用户注册
 */
export function register(data: {
  username: string
  email: string
  password: string
  password_confirm: string
  phone?: string
}) {
  return request.post('/auth/register/', data)
}

/**
 * 用户登出
 */
export function logout() {
  return request.post('/auth/logout/')
}

/**
 * 刷新Token
 */
export function refreshToken(refresh: string) {
  return request.post('/auth/token/refresh/', { refresh })
}

// ==================== 用户信息 ====================

/**
 * 获取当前用户信息
 */
export function getUserInfo() {
  return request.get('/users/me/')
}

/**
 * 获取用户画像
 */
export function getProfile() {
  return request.get<UserProfile>('/users/profile/')
}

/**
 * 更新用户画像
 */
export function updateProfile(data: Partial<UserProfile>) {
  return request.patch<UserProfile>('/users/profile/', data)
}

/**
 * 创建用户画像
 */
export function createProfile(data: Partial<UserProfile>) {
  return request.post<UserProfile>('/users/profile/create/', data)
}
