"""
职位模块管理后台配置
"""

from django.contrib import admin
from .models import JobCategory, JobTag, Company, Job


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    """职位分类管理"""
    list_display = ['name', 'parent', 'sort_order']
    list_filter = ['parent']
    search_fields = ['name']


@admin.register(JobTag)
class JobTagAdmin(admin.ModelAdmin):
    """职位标签管理"""
    list_display = ['name', 'category', 'color']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """公司管理"""
    list_display = ['name', 'size', 'industry', 'financing_stage']
    list_filter = ['size', 'financing_stage']
    search_fields = ['name', 'industry']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """职位管理"""
    list_display = ['title', 'company', 'location', 'get_salary_range', 'education_required', 'experience_required', 'is_active']
    list_filter = ['is_active', 'is_urgent', 'is_hot', 'education_required', 'experience_required']
    search_fields = ['title', 'company__name', 'location']
    raw_id_fields = ['company', 'category']
    filter_horizontal = ['tags']

    def get_salary_range(self, obj):
        return obj.get_salary_range()
    get_salary_range.short_description = '薪资范围'
