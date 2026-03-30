<!--
  推荐页面
  展示个性化推荐结果

  作者: 刘怀仁
-->

<template>
  <div class="recommendations-page">
    <div class="page-header">
      <h1>个性化推荐</h1>
      <p>基于您的画像和行为，为您精选以下职位</p>
    </div>

    <!-- 用户画像提示 -->
    <div v-if="!userStore.isProfileComplete" class="profile-notice">
      <el-alert
        title="完善您的个人信息可以获得更精准的推荐"
        type="info"
        :closable="false"
        show-icon
      >
        <template #default>
          <el-button type="primary" size="small" @click="goToProfile">
            完善信息
          </el-button>
        </template>
      </el-alert>
    </div>

    <!-- 推荐列表 -->
    <div class="recommendations-list" v-loading="loading">
      <template v-if="recommendations.length > 0">
        <div
          v-for="rec in recommendations"
          :key="rec.id"
          class="recommendation-item"
          @click="goToDetail(rec.id)"
        >
          <JobCard :job="rec" :show-reason="true" />

          <!-- 推荐理由 -->
          <div class="match-info" v-if="rec.match_reasons?.length">
            <div class="match-score">
              <span class="score-label">匹配度</span>
              <el-progress
                :percentage="Math.round(rec.match_score * 100)"
                :stroke-width="10"
                :color="getScoreColor(rec.match_score)"
              />
            </div>
            <div class="match-reasons">
              <el-tag
                v-for="reason in rec.match_reasons.slice(0, 3)"
                :key="reason.type"
                size="small"
                effect="light"
                class="reason-tag"
              >
                {{ reason.desc }}
              </el-tag>
            </div>
          </div>
        </div>
      </template>
      <el-empty v-else description="暂无推荐，请完善个人信息或浏览更多职位" />
    </div>

    <!-- 刷新按钮 -->
    <div class="refresh-btn">
      <el-button @click="fetchRecommendations" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新推荐
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import JobCard from '@/components/job/JobCard.vue'
import { getRecommendations } from '@/api/recommendation'
import type { Job } from '@/types/job'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const recommendations = ref<Job[]>([])

async function fetchRecommendations() {
  loading.value = true
  try {
    const response = await getRecommendations(20)
    recommendations.value = response.recommendations || response
  } catch (error) {
    console.error('获取推荐失败:', error)
  } finally {
    loading.value = false
  }
}

function getScoreColor(score: number): string {
  if (score >= 0.8) return '#67c23a'
  if (score >= 0.6) return '#409eff'
  if (score >= 0.4) return '#e6a23c'
  return '#f56c6c'
}

function goToDetail(id: number) {
  router.push(`/jobs/${id}`)
}

function goToProfile() {
  router.push('/profile')
}

onMounted(() => {
  fetchRecommendations()
})
</script>

<style scoped>
.recommendations-page {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  margin-bottom: 8px;
}

.page-header p {
  color: #909399;
}

.profile-notice {
  margin-bottom: 20px;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 400px;
}

.recommendation-item {
  cursor: pointer;
}

.match-info {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.match-score {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.score-label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.match-score .el-progress {
  flex: 1;
}

.match-reasons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.reason-tag {
  margin: 0;
}

.refresh-btn {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>
