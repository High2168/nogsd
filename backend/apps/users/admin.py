"""
用户模块管理后台配置
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    """用户画像内联管理"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户画像'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理"""
    list_display = ['username', 'email', 'phone', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'phone']
    ordering = ['-date_joined']
    inlines = [UserProfileInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用户画像管理"""
    list_display = ['user', 'name', 'education', 'expected_position', 'work_experience']
    list_filter = ['education', 'gender', 'job_type']
    search_fields = ['user__username', 'name', 'school', 'major']
