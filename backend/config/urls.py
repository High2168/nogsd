"""
Django项目URL配置
定义项目的URL路由
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Django管理后台
    path('admin/', admin.site.urls),

    # API路由
    path('api/auth/', include('apps.users.urls')),          # 用户认证
    path('api/users/', include('apps.users.urls')),         # 用户管理
    path('api/jobs/', include('apps.jobs.urls')),           # 职位管理
    path('api/recommendations/', include('apps.recommendations.urls')),  # 推荐

    # API文档
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# 开发环境下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
