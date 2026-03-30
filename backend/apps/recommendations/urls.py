"""
推荐模块URL配置
定义推荐相关的API路由

作者: 刘怀仁
"""

from django.urls import path
from . import views

urlpatterns = [
    # 获取推荐
    path('', views.RecommendationListView.as_view(), name='recommendations'),

    # 创建交互记录
    path('interact/', views.InteractionCreateView.as_view(), name='interact'),

    # 用户收藏列表
    path('favorites/', views.UserFavoritesView.as_view(), name='favorites'),

    # 用户交互历史
    path('history/', views.UserInteractionsView.as_view(), name='history'),
]
