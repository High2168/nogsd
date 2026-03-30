<!--
  职位卡片组件
  展示职位简要信息

  作者: 刘怀仁
-->

<template>
  <div class="job-card" @click="handleClick">
    <!-- 匹配度徽章 -->
    <div v-if="showScore && job.match_score" class="match-badge">
      <span class="score">{{ Math.round(job.match_score * 100) }}%</span>
      <span class="label">匹配</span>
    </div>

    <!-- 职位信息 -->
    <div class="job-main">
      <h3 class="job-title">{{ job.title }}</h3>
      <div class="company-info">
        <span class="company-name">{{ job.company_name || job.company?.name }}</span>
        <span class="company-tag" v-if="job.company_size">{{ job.company_size }}</span>
        <span class="company-tag" v-if="job.company_industry">{{ job.company_industry }}</span>
      </div>

      <div class="job-meta">
        <span class="salary">{{ job.salary_range || formatSalary(job.salary_min, job.salary_max) }}</span>
        <span class="location">
          <el-icon><Location /></el-icon>
          {{ job.location }}
        </span>
        <span class="education">{{ getEducationLabel(job.education_required) }}</span>
        <span class="experience">{{ getExperienceLabel(job.experience_required) }}</span>
      </div>

      <!-- 技能标签 -->
      <div class="skill-tags" v-if="job.skill_tags?.length">
        <el-tag
          v-for="tag in job.skill_tags.slice(0, 5)"
          :key="tag.id"
          size="small"
          effect="light"
        >
          {{ tag.name }}
        </el-tag>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="job-actions" @click.stop>
      <el-button
        :type="isFavorite ? 'danger' : 'default'"
        :icon="isFavorite ? StarFilled : Star"
        circle
        @click="toggleFavorite"
      />
    </div>

    <!-- 热门/紧急标签 -->
    <div class="job-badges">
      <el-tag v-if="job.is_hot" type="danger" size="small" effect="dark">热门</el-tag>
      <el-tag v-if="job.is_urgent" type="warning" size="small" effect="dark">急聘</el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Location, Star, StarFilled } from '@element-plus/icons-vue'
import type { Job } from '@/types/job'
import { favoriteJob, unfavoriteJob } from '@/api/recommendation'
import { ElMessage } from 'element-plus'

interface Props {
  job: Job
  showScore?: boolean
  showReason?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showScore: false,
  showReason: false,
})

const emit = defineEmits<{
  (e: 'click', job: Job): void
  (e: 'favorite-change', jobId: number, isFavorite: boolean): void
}>()

// 使用本地 ref 跟踪收藏状态，避免直接修改 props
const isFavorite = ref(props.job.is_favorite)

// 监听 props 变化同步本地状态
watch(
  () => props.job.is_favorite,
  (newVal) => {
    isFavorite.value = newVal
  }
)

function formatSalary(min: number, max: number): string {
  return `${Math.round(min / 1000)}K-${Math.round(max / 1000)}K`
}

function getEducationLabel(value: string): string {
  const map: Record<string, string> = {
    unlimited: '学历不限',
    high_school: '高中',
    college: '大专',
    bachelor: '本科',
    master: '硕士',
    doctor: '博士',
  }
  return map[value] || value
}

function getExperienceLabel(value: string): string {
  const map: Record<string, string> = {
    unlimited: '经验不限',
    '0-1': '应届/0-1年',
    '1-3': '1-3年',
    '3-5': '3-5年',
    '5-10': '5-10年',
    '10+': '10年以上',
  }
  return map[value] || value
}

function handleClick() {
  emit('click', props.job)
}

async function toggleFavorite(): Promise<void> {
  try {
    const newFavoriteState = !isFavorite.value

    if (isFavorite.value) {
      await unfavoriteJob(props.job.id)
    } else {
      await favoriteJob(props.job.id)
    }

    // 更新本地状态
    isFavorite.value = newFavoriteState

    // 通知父组件状态变化
    emit('favorite-change', props.job.id, newFavoriteState)
  } catch (error) {
    // 错误时恢复原状态
    isFavorite.value = props.job.is_favorite
    ElMessage.error('收藏操作失败，请重试')
  }
}
</script>

<style scoped>
.job-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  display: flex;
  gap: 16px;
}

.job-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.match-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  text-align: center;
}

.match-badge .score {
  font-size: 16px;
  font-weight: bold;
}

.match-badge .label {
  font-size: 12px;
  display: block;
}

.job-main {
  flex: 1;
}

.job-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.company-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.company-name {
  color: #606266;
}

.company-tag {
  font-size: 12px;
  color: #909399;
  padding: 2px 8px;
  background: #f4f4f5;
  border-radius: 4px;
}

.job-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 12px;
  color: #909399;
  font-size: 14px;
}

.job-meta .salary {
  color: #f56c6c;
  font-weight: 600;
  font-size: 16px;
}

.job-meta .location {
  display: flex;
  align-items: center;
  gap: 4px;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.job-actions {
  display: flex;
  align-items: flex-start;
}

.job-badges {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  gap: 4px;
}
</style>
