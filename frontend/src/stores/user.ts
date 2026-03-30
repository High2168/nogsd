/**
 * 用户状态管理
 * 使用Pinia管理用户状态
 *
 * 作者: 刘怀仁
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserProfile } from '@/types/user'
import * as userApi from '@/api/user'

export const useUserStore = defineStore('user', () => {
  // ==================== 状态 ====================
  // 用户信息
  const user = ref<{
    id: number
    username: string
    email: string
    phone?: string
    avatar?: string
  } | null>(null)

  // 用户画像
  const profile = ref<UserProfile | null>(null)

  // Token
  const token = ref<string | null>(localStorage.getItem('token'))

  // 加载状态
  const loading = ref(false)

  // ==================== 计算属性 ====================
  // 是否已登录
  const isAuthenticated = computed(() => !!token.value)

  // 用户画像是否完整
  const isProfileComplete = computed(() => {
    if (!profile.value) return false
    return !!(profile.value.name && profile.value.expected_position)
  })

  // ==================== 方法 ====================

  /**
   * 用户登录
   */
  async function login(
    username: string,
    password: string
  ): Promise<{ user: { id: number; username: string; email: string }; token: { access: string; refresh: string } }> {
    loading.value = true
    try {
      const response = await userApi.login({ username, password })
      user.value = response.user
      token.value = response.token.access
      localStorage.setItem('token', response.token.access)
      localStorage.setItem('refreshToken', response.token.refresh)
      return response
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户注册
   */
  async function register(data: {
    username: string
    email: string
    password: string
    password_confirm: string
  }): Promise<{ user: { id: number; username: string; email: string }; token: { access: string; refresh: string } }> {
    loading.value = true
    try {
      const response = await userApi.register(data)
      user.value = response.user
      token.value = response.token.access
      localStorage.setItem('token', response.token.access)
      localStorage.setItem('refreshToken', response.token.refresh)
      return response
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户登出
   */
  function logout(): void {
    user.value = null
    profile.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  /**
   * 获取用户信息
   */
  async function fetchUser(): Promise<void> {
    if (!token.value) return
    loading.value = true
    try {
      const response = await userApi.getUserInfo()
      user.value = response
    } catch (error) {
      logout()
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取用户画像
   */
  async function fetchProfile(): Promise<void> {
    if (!token.value) return
    loading.value = true
    try {
      const response = await userApi.getProfile()
      profile.value = response
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新用户画像
   */
  async function updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    loading.value = true
    try {
      const response = await userApi.updateProfile(data)
      profile.value = response
      return response
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    user,
    profile,
    token,
    loading,
    // 计算属性
    isAuthenticated,
    isProfileComplete,
    // 方法
    login,
    register,
    logout,
    fetchUser,
    fetchProfile,
    updateProfile,
  }
})
