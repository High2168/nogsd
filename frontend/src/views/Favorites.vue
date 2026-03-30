<!-- 我的收藏页面 -->
<template>
  <div class="favorites-page">
    <h1>我的收藏</h1>
    <div class="job-list" v-loading="loading">
      <template v-if="jobs.length > 0">
        <JobCard v-for="job in jobs" :key="job.id" :job="job" @click="goToDetail(job.id)" />
      </template>
      <el-empty v-else description="暂无收藏" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import JobCard from '@/components/job/JobCard.vue'
import { getFavorites } from '@/api/recommendation'
import type { Job } from '@/types/job'

const router = useRouter()
const loading = ref(false)
const jobs = ref<Job[]>([])

async function loadFavorites() {
  loading.value = true
  try {
    jobs.value = await getFavorites()
  } finally {
    loading.value = false
  }
}

function goToDetail(id: number) {
  router.push(`/jobs/${id}`)
}

onMounted(() => {
  loadFavorites()
})
</script>

<style scoped>
.favorites-page {
  max-width: 900px;
  margin: 0 auto;
}
.job-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
