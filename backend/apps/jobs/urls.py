"""
职位模块URL配置
定义职位相关的API路由

作者: 刘怀仁
"""

from django.urls import path
from . import views

urlpatterns = [
    # 职位列表
    path('', views.JobListView.as_view(), name='job_list'),

    # 职位详情
    path('<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),

    # 职位搜索
    path('search/', views.JobSearchView.as_view(), name='job_search'),

    # 热门职位
    path('hot/', views.HotJobListView.as_view(), name='hot_jobs'),

    # 职位分类
    path('categories/', views.JobCategoryListView.as_view(), name='job_categories'),

    # 职位标签
    path('tags/', views.JobTagListView.as_view(), name='job_tags'),
]
