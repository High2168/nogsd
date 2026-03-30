<!--
  职位列表页面
  展示职位列表，支持搜索和筛选
-->

<template>
  <div class="job-list-page">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索职位名称、公司名称"
        clearable
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #append>
          <el-button @click="handleSearch">搜索</el-button>
        </template>
      </el-input>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-bar">
      <el-select v-model="filters.location" placeholder="城市" clearable @change="handleFilter">
        <el-option
          v-for="city in cities"
          :key="city"
          :label="city"
          :value="city"
        />
      </el-select>

      <el-select v-model="filters.education" placeholder="学历要求" clearable @change="handleFilter">
        <el-option label="不限" value="unlimited" />
        <el-option label="大专" value="college" />
        <el-option label="本科" value="bachelor" />
        <el-option label="硕士" value="master" />
        <el-option label="博士" value="doctor" />
      </el-select>

      <el-select v-model="filters.experience" placeholder="经验要求" clearable @change="handleFilter">
        <el-option label="不限" value="unlimited" />
        <el-option label="应届生" value="0-1" />
        <el-option label="1-3年" value="1-3" />
        <el-option label="3-5年" value="3-5" />
        <el-option label="5-10年" value="5-10" />
      </el-select>

      <el-select v-model="filters.salaryRange" placeholder="薪资范围" clearable @change="handleFilter">
        <el-option label="不限" value="" />
        <el-option label="10K以下" value="0-10000" />
        <el-option label="10-20K" value="10000-20000" />
        <el-option label="20-30K" value="20000-30000" />
        <el-option label="30K以上" value="30000-100000" />
      </el-select>
    </div>

    <!-- 职位列表 -->
    <div class="job-list" v-loading="loading">
      <template v-if="jobs.length > 0">
        <JobCard
          v-for="job in jobs"
          :key="job.id"
          :job="job"
          @click="goToDetail(job.id)"
        />
      </template>
      <el-empty v-else description="暂无符合条件的职位" />
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import JobCard from '@/components/job/JobCard.vue'
import { getJobs } from '@/api/job'
import type { Job, JobSearchParams } from '@/types/job'

const router = useRouter()

const loading = ref(false)
const jobs = ref<Job[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20

const searchKeyword = ref('')
const filters = reactive({
  location: '',
  education: '',
  experience: '',
  salaryRange: '',
})

const cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉']

// 获取职位列表
async function fetchJobs(): Promise<void> {
  loading.value = true
  try {
    const params: JobSearchParams = {
      page: currentPage.value,
      page_size: pageSize,
    }

    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    if (filters.location) {
      params.location = filters.location
    }
    if (filters.education) {
      params.education = filters.education
    }
    if (filters.experience) {
      params.experience = filters.experience
    }
    if (filters.salaryRange) {
      const [min, max] = filters.salaryRange.split('-')
      params.salary_min = Number(min)
      params.salary_max = Number(max)
    }

    const response = await getJobs(params)
    jobs.value = response.results
    total.value = response.count
  } catch (error) {
    console.error('获取职位列表失败:', error)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
  fetchJobs()
}

function handleFilter() {
  currentPage.value = 1
  fetchJobs()
}

function handlePageChange(page: number) {
  currentPage.value = page
  fetchJobs()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToDetail(id: number) {
  router.push(`/jobs/${id}`)
}

onMounted(() => {
  fetchJobs()
})
</script>

<style scoped>
.job-list-page {
  max-width: 1000px;
  margin: 0 auto;
}

.search-bar {
  margin-bottom: 20px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-bar .el-select {
  width: 140px;
}

.job-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 400px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>
