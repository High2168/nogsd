<!-- 个人中心页面 -->
<template>
  <div class="profile-page">
    <h1>个人中心</h1>
    <el-card v-loading="loading">
      <template #header>
        <span>基本信息</span>
      </template>
      <el-form :model="profile" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名">
              <el-input v-model="profile.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别">
              <el-radio-group v-model="profile.gender">
                <el-radio label="male">男</el-radio>
                <el-radio label="female">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学历">
              <el-select v-model="profile.education" placeholder="请选择">
                <el-option label="大专" value="college" />
                <el-option label="本科" value="bachelor" />
                <el-option label="硕士" value="master" />
                <el-option label="博士" value="doctor" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="毕业院校">
              <el-input v-model="profile.school" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="期望职位">
          <el-input v-model="profile.expected_position" />
        </el-form-item>
        <el-form-item label="期望薪资">
          <el-slider v-model="salaryRange" range :min="5" :max="100" :step="1" :format-tooltip="formatSalary" />
        </el-form-item>
        <el-form-item label="期望城市">
          <el-select v-model="profile.expected_cities" multiple placeholder="请选择城市">
            <el-option v-for="city in cities" :key="city" :label="city" :value="city" />
          </el-select>
        </el-form-item>
        <el-form-item label="技能标签">
          <el-select v-model="selectedSkills" multiple filterable placeholder="选择技能">
            <el-option v-for="skill in skills" :key="skill" :label="skill" :value="skill" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveProfile" :loading="saving">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import type { UserProfile } from '@/types/user'

const userStore = useUserStore()
const loading = ref(false)
const saving = ref(false)

const profile = reactive<Partial<UserProfile>>({
  name: '',
  gender: 'male',
  education: '',
  school: '',
  expected_position: '',
  expected_cities: [],
})

const salaryRange = ref([15, 35])
const selectedSkills = ref<string[]>([])

const cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉']
const skills = ['Python', 'Java', 'JavaScript', 'Vue', 'React', 'Django', 'MySQL', 'Redis']

function formatSalary(val: number) {
  return `${val}K`
}

async function loadProfile() {
  loading.value = true
  try {
    await userStore.fetchProfile()
    if (userStore.profile) {
      Object.assign(profile, userStore.profile)
      if (profile.expected_salary_min && profile.expected_salary_max) {
        salaryRange.value = [profile.expected_salary_min / 1000, profile.expected_salary_max / 1000]
      }
    }
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  saving.value = true
  try {
    profile.expected_salary_min = salaryRange.value[0] * 1000
    profile.expected_salary_max = salaryRange.value[1] * 1000
    profile.skills = selectedSkills.value.map(name => ({ name, level: 3 }))
    await userStore.updateProfile(profile)
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-page {
  max-width: 800px;
  margin: 0 auto;
}
</style>
