"""
用户模块URL配置
定义用户相关的API路由

作者: 刘怀仁
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # ==================== 认证相关 ====================
    # 用户注册
    path('register/', views.UserRegisterView.as_view(), name='register'),

    # 用户登录
    path('login/', views.UserLoginView.as_view(), name='login'),

    # 用户登出
    path('logout/', views.UserLogoutView.as_view(), name='logout'),

    # 刷新Token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ==================== 用户信息 ====================
    # 当前用户信息
    path('me/', views.UserDetailView.as_view(), name='user_detail'),

    # 用户画像
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),

    # 创建用户画像
    path('profile/create/', views.UserProfileCreateView.as_view(), name='user_profile_create'),
]
