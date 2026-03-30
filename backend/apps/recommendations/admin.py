"""
推荐模块管理后台配置
"""

from django.contrib import admin
from .models import UserJobInteraction, Recommendation, UserSimilarity, JobSimilarity


@admin.register(UserJobInteraction)
class UserJobInteractionAdmin(admin.ModelAdmin):
    """用户交互记录管理"""
    list_display = ['user', 'job', 'interaction_type', 'rating', 'created_at']
    list_filter = ['interaction_type', 'created_at']
    search_fields = ['user__username', 'job__title']
    raw_id_fields = ['user', 'job']


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    """推荐结果管理"""
    list_display = ['user', 'job', 'score', 'algorithm', 'is_viewed', 'is_interacted', 'created_at']
    list_filter = ['algorithm', 'is_viewed', 'is_interacted', 'created_at']
    search_fields = ['user__username', 'job__title']
    raw_id_fields = ['user', 'job']


@admin.register(UserSimilarity)
class UserSimilarityAdmin(admin.ModelAdmin):
    """用户相似度管理"""
    list_display = ['user1', 'user2', 'similarity', 'calculated_at']
    search_fields = ['user1__username', 'user2__username']
    raw_id_fields = ['user1', 'user2']


@admin.register(JobSimilarity)
class JobSimilarityAdmin(admin.ModelAdmin):
    """职位相似度管理"""
    list_display = ['job1', 'job2', 'similarity', 'calculated_at']
    search_fields = ['job1__title', 'job2__title']
    raw_id_fields = ['job1', 'job2']
