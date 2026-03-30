<!--
  首页视图
  展示热门职位和推荐入口

  作者: 刘怀仁
-->

<template>
  <div class="home-page">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-content">
        <h1>智能就业推荐系统</h1>
        <p>基于协同过滤算法，为您精准匹配理想职位</p>
        <div class="banner-actions">
          <el-button type="primary" size="large" @click="goToRecommendations">
            获取推荐
          </el-button>
          <el-button size="large" @click="goToJobs">
            浏览职位
          </el-button>
        </div>
      </div>
    </div>

    <!-- 热门职位 -->
    <section class="section">
      <div class="section-header">
        <h2>热门职位</h2>
        <el-button text @click="goToJobs">查看更多 ></el-button>
      </div>
      <div class="job-grid" v-loading="loading">
        <JobCard
          v-for="job in hotJobs"
          :key="job.id"
          :job="job"
          @click="goToJobDetail(job.id)"
        />
      </div>
    </section>

    <!-- 功能介绍 -->
    <section class="section features">
      <h2>系统特色</h2>
      <div class="feature-grid">
        <div class="feature-item">
          <el-icon :size="48" color="#409eff"><MagicStick /></el-icon>
          <h3>智能推荐</h3>
          <p>基于协同过滤算法，分析用户行为偏好，精准推荐合适职位</p>
        </div>
        <div class="feature-item">
          <el-icon :size="48" color="#67c23a"><UserFilled /></el-icon>
          <h3>用户画像</h3>
          <p>构建多维用户画像，结合技能、期望、经验等特征提升推荐质量</p>
        </div>
        <div class="feature-item">
          <el-icon :size="48" color="#e6a23c"><TrendCharts /></el-icon>
          <h3>数据分析</h3>
          <p>可视化展示推荐结果与匹配理由，帮助用户理解推荐逻辑</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { MagicStick, UserFilled, TrendCharts } from '@element-plus/icons-vue'
import JobCard from '@/components/job/JobCard.vue'
import { getHotJobs } from '@/api/job'
import type { Job } from '@/types/job'

const router = useRouter()
const loading = ref(false)
const hotJobs = ref<Job[]>([])

// 获取热门职位
async function fetchHotJobs() {
  loading.value = true
  try {
    const response = await getHotJobs()
    hotJobs.value = response.results || response
  } catch (error) {
    console.error('获取热门职位失败:', error)
  } finally {
    loading.value = false
  }
}

// 导航方法
function goToRecommendations() {
  router.push('/recommendations')
}

function goToJobs() {
  router.push('/jobs')
}

function goToJobDetail(id: number) {
  router.push(`/jobs/${id}`)
}

onMounted(() => {
  fetchHotJobs()
})
</script>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-banner {
  background: linear-gradient(135deg, #409eff 0%, #667eea 100%);
  border-radius: 16px;
  padding: 60px 40px;
  margin-bottom: 40px;
  color: white;
  text-align: center;
}

.banner-content h1 {
  font-size: 36px;
  margin-bottom: 16px;
}

.banner-content p {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 24px;
}

.banner-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 24px;
  color: #303133;
}

.job-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.features h2 {
  text-align: center;
  margin-bottom: 30px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}

.feature-item {
  text-align: center;
  padding: 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.feature-item h3 {
  margin: 16px 0 8px;
  font-size: 18px;
}

.feature-item p {
  color: #606266;
  font-size: 14px;
}

@media (max-width: 768px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
}
</style>
