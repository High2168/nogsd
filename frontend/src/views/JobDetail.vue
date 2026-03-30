<!-- 职位详情页面 -->
<template>
  <div class="job-detail-page" v-loading="loading">
    <template v-if="job">
      <div class="job-header">
        <h1>{{ job.title }}</h1>
        <div class="salary">{{ job.salary_range }}</div>
        <div class="meta">
          <span><el-icon><Location /></el-icon> {{ job.location }}</span>
          <span>{{ job.education_required }}</span>
          <span>{{ job.experience_required }}</span>
        </div>
        <div class="actions">
          <el-button type="primary" @click="handleApply">投递简历</el-button>
          <el-button :type="job.is_favorite ? 'danger' : 'default'" @click="toggleFavorite">
            {{ job.is_favorite ? '已收藏' : '收藏' }}
          </el-button>
        </div>
      </div>

      <el-card class="company-card">
        <template #header>公司信息</template>
        <div class="company">
          <h3>{{ job.company?.name }}</h3>
          <p>{{ job.company?.industry }} | {{ job.company?.size }}</p>
        </div>
      </el-card>

      <el-card class="desc-card">
        <template #header>职位描述</template>
        <div class="description" v-html="formatDesc(job.description)"></div>
      </el-card>

      <el-card class="tags-card">
        <template #header>技能要求</template>
        <div class="tags">
          <el-tag v-for="tag in job.skill_tags" :key="tag.id" effect="light">{{ tag.name }}</el-tag>
        </div>
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Location } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getJobDetail } from '@/api/job'
import { favoriteJob, unfavoriteJob, applyJob } from '@/api/recommendation'
import type { Job } from '@/types/job'

const route = useRoute()
const loading = ref(false)
const job = ref<Job | null>(null)

async function loadJob() {
  loading.value = true
  try {
    const id = Number(route.params.id)
    job.value = await getJobDetail(id)
  } catch (error) {
    ElMessage.error('职位不存在')
  } finally {
    loading.value = false
  }
}

function formatDesc(desc: string) {
  return desc?.replace(/\n/g, '<br>') || ''
}

async function toggleFavorite() {
  if (!job.value) return
  try {
    if (job.value.is_favorite) {
      await unfavoriteJob(job.value.id)
      job.value.is_favorite = false
      ElMessage.success('已取消收藏')
    } else {
      await favoriteJob(job.value.id)
      job.value.is_favorite = true
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleApply() {
  if (!job.value) return
  try {
    await applyJob(job.value.id)
    ElMessage.success('投递成功')
  } catch (error) {
    ElMessage.error('投递失败')
  }
}

onMounted(() => {
  loadJob()
})
</script>

<style scoped>
.job-detail-page {
  max-width: 800px;
  margin: 0 auto;
}
.job-header {
  background: white;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 20px;
}
.job-header h1 {
  font-size: 28px;
  margin-bottom: 12px;
}
.salary {
  color: #f56c6c;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 12px;
}
.meta {
  color: #909399;
  margin-bottom: 20px;
}
.meta span {
  margin-right: 20px;
}
.actions {
  display: flex;
  gap: 12px;
}
.company-card, .desc-card, .tags-card {
  margin-bottom: 20px;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
